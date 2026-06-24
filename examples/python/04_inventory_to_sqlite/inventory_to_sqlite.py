#!/usr/bin/env python3
"""Parse sources from an inventory database and store AST nodes in SQLite.

This is an application-level pattern, not native-library responsibility:

- SQLite inventory and output are owned by Python.
- Source files are read by Python workers.
- FastParse receives source bytes in RAM and returns MessagePack bytes in RAM.
- Python decodes the MessagePack payload into dataclasses and persists rows.
"""

from __future__ import annotations

import argparse
import os
import queue
import sqlite3
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from fastparse import FastParse, OutputFormat, ParseOptions, default_library_path  # noqa: E402


DEFAULT_INVENTORY_DB = Path(
    "/Users/natanbarronlugo/Desktop/Proyectos/appbatch/"
    "migracion_utilerias_sysmining/inventario_componentes/db/inventario.db"
)
DEFAULT_SOURCE_ROOT = Path(
    "/Users/natanbarronlugo/Desktop/Proyectos/appbatch/"
    "migracion_utilerias_sysmining/componentes"
)


@dataclass(frozen=True)
class InventoryItem:
    name: str
    relative_path: str
    inventory_lines: int | None
    source_path: Path


@dataclass(frozen=True)
class FileMetrics:
    file_key: str
    component_name: str
    inventory_path: str
    source_path: str
    language: str
    source_bytes: int
    source_lines: int
    inventory_lines: int | None
    ok: int
    elapsed_ms: float
    node_count: int
    ast_bytes: int
    has_errors: int | None
    error_node_count: int | None
    missing_node_count: int | None
    error_byte_count: int | None
    error: str


_STOP = object()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse files listed in an inventory SQLite DB and write AST rows to another SQLite DB."
    )
    parser.add_argument("--inventory-db", type=Path, default=DEFAULT_INVENTORY_DB)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--out-db", type=Path, default=ROOT / "exports" / "fastparse_python_ast.sqlite")
    parser.add_argument("--lib", type=Path, default=default_library_path())
    parser.add_argument("--language", default="java")
    parser.add_argument("--type", dest="file_type", default="", help="Filter componentes.tipo_archivo, e.g. COBOL.")
    parser.add_argument("--extension", default="java", help="Filter componentes.extension. Empty disables this filter.")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--rules", default="", help="Pipe-separated rules. Empty means all AST rules.")
    parser.add_argument("--fields", default="", help="Comma-separated fields. Empty means all fields.")
    parser.add_argument("--normalization", default="auto_safe")
    parser.add_argument("--language-extension", type=Path, help="Optional FastParse language extension library.")
    parser.add_argument("--batch-size", type=int, default=2000)
    parser.add_argument("--no-store-nodes", action="store_true")
    parser.add_argument("--no-store-children", action="store_true")
    parser.add_argument("--busy-timeout-ms", type=int, default=30000)
    return parser.parse_args()


def count_lines(source: bytes) -> int:
    if not source:
        return 0
    return source.count(b"\n") + (0 if source.endswith(b"\n") else 1)


def resolve_source_path(source_root: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        return candidate
    return source_root / candidate


def load_inventory(args: argparse.Namespace) -> list[InventoryItem]:
    clauses: list[str] = []
    values: list[object] = []
    if args.file_type:
        clauses.append("tipo_archivo = ?")
        values.append(args.file_type)
    if args.extension:
        clauses.append("lower(coalesce(extension, '')) = lower(?)")
        values.append(args.extension)
    where = f"where {' and '.join(clauses)}" if clauses else ""
    limit = "limit ?" if args.limit > 0 else ""
    if args.limit > 0:
        values.append(args.limit)

    sql = (
        "select nombre, ruta_relativa, num_lineas "
        f"from componentes {where} "
        "order by ruta_relativa "
        f"{limit}"
    )
    with sqlite3.connect(args.inventory_db) as conn:
        rows = conn.execute(sql, values).fetchall()

    return [
        InventoryItem(
            name=str(name),
            relative_path=str(relative_path),
            inventory_lines=int(num_lineas) if num_lineas is not None else None,
            source_path=resolve_source_path(args.source_root, str(relative_path)),
        )
        for name, relative_path, num_lineas in rows
    ]


def setup_output_db(conn: sqlite3.Connection, busy_timeout_ms: int) -> None:
    conn.execute(f"pragma busy_timeout = {busy_timeout_ms}")
    conn.execute("pragma journal_mode = wal")
    conn.execute("pragma synchronous = normal")
    conn.executescript(
        """
        create table if not exists parse_files (
            file_key text primary key,
            component_name text not null,
            inventory_path text not null,
            source_path text not null,
            language text not null,
            source_bytes integer not null,
            source_lines integer not null,
            inventory_lines integer,
            ok integer not null,
            elapsed_ms real not null,
            node_count integer not null,
            ast_bytes integer not null,
            has_errors integer,
            error_node_count integer,
            missing_node_count integer,
            error_byte_count integer,
            error text not null,
            parsed_at text not null default current_timestamp
        );

        create table if not exists ast_nodes (
            id integer primary key autoincrement,
            file_key text not null,
            node_id integer,
            parent_id integer,
            rule text,
            text blob,
            start_line integer,
            start_column integer,
            end_line integer,
            end_column integer,
            start_byte integer,
            end_byte integer,
            child_count integer,
            is_error integer,
            is_missing integer,
            has_error integer
        );

        create table if not exists ast_children (
            id integer primary key autoincrement,
            file_key text not null,
            node_id integer,
            child_index integer not null,
            rule text,
            text blob
        );

        create index if not exists ix_ast_nodes_file_rule on ast_nodes(file_key, rule);
        create index if not exists ix_ast_nodes_rule on ast_nodes(rule);
        create index if not exists ix_ast_nodes_parent on ast_nodes(file_key, parent_id);
        create index if not exists ix_ast_children_node on ast_children(file_key, node_id);
        """
    )


def write_loop(out_db: Path, busy_timeout_ms: int, messages: "queue.Queue[object]") -> None:
    out_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(out_db) as conn:
        setup_output_db(conn, busy_timeout_ms)
        while True:
            message = messages.get()
            try:
                if message is _STOP:
                    conn.commit()
                    return
                kind, payload = message  # type: ignore[misc]
                if kind == "file":
                    metric: FileMetrics = payload
                    conn.execute(
                        """
                        insert or replace into parse_files (
                            file_key, component_name, inventory_path, source_path, language,
                            source_bytes, source_lines, inventory_lines, ok, elapsed_ms,
                            node_count, ast_bytes, has_errors, error_node_count,
                            missing_node_count, error_byte_count, error
                        )
                        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            metric.file_key,
                            metric.component_name,
                            metric.inventory_path,
                            metric.source_path,
                            metric.language,
                            metric.source_bytes,
                            metric.source_lines,
                            metric.inventory_lines,
                            metric.ok,
                            metric.elapsed_ms,
                            metric.node_count,
                            metric.ast_bytes,
                            metric.has_errors,
                            metric.error_node_count,
                            metric.missing_node_count,
                            metric.error_byte_count,
                            metric.error,
                        ),
                    )
                elif kind == "nodes":
                    conn.executemany(
                        """
                        insert into ast_nodes (
                            file_key, node_id, parent_id, rule, text,
                            start_line, start_column, end_line, end_column,
                            start_byte, end_byte, child_count,
                            is_error, is_missing, has_error
                        )
                        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        payload,
                    )
                elif kind == "children":
                    conn.executemany(
                        """
                        insert into ast_children (file_key, node_id, child_index, rule, text)
                        values (?, ?, ?, ?, ?)
                        """,
                        payload,
                    )
            finally:
                messages.task_done()


def chunked(items: Iterable[tuple], batch_size: int) -> Iterable[list[tuple]]:
    batch: list[tuple] = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def bool_int(value: bool | None) -> int | None:
    return None if value is None else int(value)


class WorkerContext(threading.local):
    parser: FastParse | None = None


def parse_item(
    item: InventoryItem,
    *,
    args: argparse.Namespace,
    thread_context: WorkerContext,
    messages: "queue.Queue[object]",
) -> FileMetrics:
    started = time.perf_counter()
    source = b""
    file_key = item.relative_path
    try:
        if thread_context.parser is None:
            thread_context.parser = FastParse(args.lib)
            if args.language_extension and not thread_context.parser.language_available(args.language):
                thread_context.parser.load_language_extension(args.language_extension)

        source = item.source_path.read_bytes()
        result = thread_context.parser.parse_bytes(
            source,
            ParseOptions(
                language=args.language,
                output_format=OutputFormat.BINARY,
                include_rules=args.rules or None,
                fields=args.fields or None,
                normalization=args.normalization,
            ),
        )
        document = result.binary_document()
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        metric = FileMetrics(
            file_key=file_key,
            component_name=item.name,
            inventory_path=item.relative_path,
            source_path=str(item.source_path),
            language=args.language,
            source_bytes=len(source),
            source_lines=count_lines(source),
            inventory_lines=item.inventory_lines,
            ok=1,
            elapsed_ms=elapsed_ms,
            node_count=result.node_count,
            ast_bytes=len(result.data),
            has_errors=bool_int(document.has_errors),
            error_node_count=document.error_node_count,
            missing_node_count=document.missing_node_count,
            error_byte_count=document.error_byte_count,
            error="",
        )
        messages.put(("file", metric))

        if not args.no_store_nodes:
            node_rows = (
                (
                    file_key,
                    node.id,
                    node.parent_id,
                    node.rule,
                    node.text,
                    node.start_line,
                    node.start_column,
                    node.end_line,
                    node.end_column,
                    node.start_byte,
                    node.end_byte,
                    node.child_count,
                    bool_int(node.is_error),
                    bool_int(node.is_missing),
                    bool_int(node.has_error),
                )
                for node in document.nodes
            )
            for batch in chunked(node_rows, args.batch_size):
                messages.put(("nodes", batch))

            if not args.no_store_children:
                child_rows = (
                    (file_key, node.id, index, child.rule, child.text)
                    for node in document.nodes
                    for index, child in enumerate(node.children)
                )
                for batch in chunked(child_rows, args.batch_size):
                    messages.put(("children", batch))

        return metric
    except Exception as exc:  # noqa: BLE001 - batch app should record per-file failures.
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        metric = FileMetrics(
            file_key=file_key,
            component_name=item.name,
            inventory_path=item.relative_path,
            source_path=str(item.source_path),
            language=args.language,
            source_bytes=len(source),
            source_lines=count_lines(source),
            inventory_lines=item.inventory_lines,
            ok=0,
            elapsed_ms=elapsed_ms,
            node_count=0,
            ast_bytes=0,
            has_errors=None,
            error_node_count=None,
            missing_node_count=None,
            error_byte_count=None,
            error=str(exc),
        )
        messages.put(("file", metric))
        return metric


def main() -> int:
    args = parse_args()
    items = load_inventory(args)
    if not items:
        print("No inventory rows matched the filters.")
        return 2

    args.out_db.unlink(missing_ok=True)
    messages: "queue.Queue[object]" = queue.Queue(maxsize=max(args.workers * 4, 16))
    writer = threading.Thread(
        target=write_loop,
        args=(args.out_db, args.busy_timeout_ms, messages),
        name="sqlite-writer",
        daemon=True,
    )
    writer.start()

    if args.language_extension:
        bootstrap = FastParse(args.lib)
        if not bootstrap.language_available(args.language):
            bootstrap.load_language_extension(args.language_extension)

    started = time.perf_counter()
    context = WorkerContext()
    results: list[FileMetrics] = []

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(parse_item, item, args=args, thread_context=context, messages=messages)
            for item in items
        ]
        for future in as_completed(futures):
            results.append(future.result())

    messages.join()
    messages.put(_STOP)
    writer.join()

    elapsed = time.perf_counter() - started
    ok = [result for result in results if result.ok]
    failed = [result for result in results if not result.ok]
    total_lines = sum(result.source_lines for result in ok)
    total_nodes = sum(result.node_count for result in ok)
    total_ast_bytes = sum(result.ast_bytes for result in ok)

    print(f"Inventory DB : {args.inventory_db}")
    print(f"Source root  : {args.source_root}")
    print(f"Output DB    : {args.out_db}")
    print(f"Language     : {args.language}")
    print(f"Workers      : {args.workers}")
    print(f"Files        : {len(results)}")
    print(f"Parsed OK    : {len(ok)}")
    print(f"Failed       : {len(failed)}")
    print(f"Lines        : {total_lines}")
    print(f"Nodes        : {total_nodes}")
    print(f"AST bytes    : {total_ast_bytes}")
    print(f"Elapsed      : {elapsed:.3f}s")
    print(f"Avg/file     : {(elapsed / len(results) * 1000.0):.3f} ms")
    print(f"Files/sec    : {(len(results) / elapsed):.1f}")
    print(f"Lines/sec    : {(total_lines / elapsed):.1f}")

    for result in failed[:10]:
        print(f"ERROR {result.inventory_path}: {result.error}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
