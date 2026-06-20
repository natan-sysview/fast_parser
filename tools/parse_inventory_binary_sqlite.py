#!/usr/bin/env python3
"""Parse Java files from the inventory DB and persist FastParse binary ASTs."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from fastparse import FastParse, default_library_path, parse_field_mask  # noqa: E402


DEFAULT_INVENTORY_DB = ROOT / "data" / "java_swing_inventory.sqlite"
DEFAULT_OUTPUT_DB = ROOT / "data" / "fastparse_java_ast_binary.sqlite"

_THREAD_LOCAL = threading.local()


@dataclass(frozen=True)
class WorkItem:
    inventory_file_id: int
    project_id: int
    project_name: str
    absolute_path: str
    root_relative_path: str
    project_relative_path: str
    file_name: str
    package_name: str
    source_bytes: int
    line_count: int
    sha256: str


@dataclass(frozen=True)
class BinaryAstSummary:
    format: str
    schema_version: int
    language: str
    node_count: int
    first_rule: str
    rule_counts: dict[str, int]


@dataclass(frozen=True)
class ParseSuccess:
    item: WorkItem
    ast_binary: bytes
    node_count: int
    binary_bytes: int
    elapsed_ms: float
    summary: BinaryAstSummary


@dataclass(frozen=True)
class ParseFailure:
    item: WorkItem
    elapsed_ms: float
    error: str


class MessagePackReader:
    """Small schema-focused MessagePack reader that skips large bin payloads."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0

    def _read_byte(self) -> int:
        if self.pos >= len(self.data):
            raise ValueError("unexpected end of MessagePack data")
        value = self.data[self.pos]
        self.pos += 1
        return value

    def _read_exact(self, size: int) -> bytes:
        end = self.pos + size
        if end > len(self.data):
            raise ValueError("unexpected end of MessagePack data")
        value = self.data[self.pos:end]
        self.pos = end
        return value

    def _skip_bytes(self, size: int) -> None:
        end = self.pos + size
        if end > len(self.data):
            raise ValueError("unexpected end of MessagePack data")
        self.pos = end

    def _read_uint_be(self, size: int) -> int:
        return int.from_bytes(self._read_exact(size), "big")

    def read_uint(self) -> int:
        prefix = self._read_byte()
        if prefix <= 0x7F:
            return prefix
        if prefix == 0xCC:
            return self._read_uint_be(1)
        if prefix == 0xCD:
            return self._read_uint_be(2)
        if prefix == 0xCE:
            return self._read_uint_be(4)
        if prefix == 0xCF:
            return self._read_uint_be(8)
        raise ValueError(f"expected uint, got MessagePack prefix 0x{prefix:02x}")

    def read_str(self) -> str:
        prefix = self._read_byte()
        if 0xA0 <= prefix <= 0xBF:
            size = prefix & 0x1F
        elif prefix == 0xD9:
            size = self._read_uint_be(1)
        elif prefix == 0xDA:
            size = self._read_uint_be(2)
        elif prefix == 0xDB:
            size = self._read_uint_be(4)
        else:
            raise ValueError(f"expected str, got MessagePack prefix 0x{prefix:02x}")
        return self._read_exact(size).decode("utf-8")

    def read_array_len(self) -> int:
        prefix = self._read_byte()
        if 0x90 <= prefix <= 0x9F:
            return prefix & 0x0F
        if prefix == 0xDC:
            return self._read_uint_be(2)
        if prefix == 0xDD:
            return self._read_uint_be(4)
        raise ValueError(f"expected array, got MessagePack prefix 0x{prefix:02x}")

    def read_map_len(self) -> int:
        prefix = self._read_byte()
        if 0x80 <= prefix <= 0x8F:
            return prefix & 0x0F
        if prefix == 0xDE:
            return self._read_uint_be(2)
        if prefix == 0xDF:
            return self._read_uint_be(4)
        raise ValueError(f"expected map, got MessagePack prefix 0x{prefix:02x}")

    def skip_value(self) -> None:
        prefix = self._read_byte()
        if prefix <= 0x7F or 0xE0 <= prefix <= 0xFF or prefix in (0xC0, 0xC2, 0xC3):
            return
        if 0xA0 <= prefix <= 0xBF:
            self.pos += prefix & 0x1F
            return
        if 0x90 <= prefix <= 0x9F:
            for _ in range(prefix & 0x0F):
                self.skip_value()
            return
        if 0x80 <= prefix <= 0x8F:
            for _ in range(prefix & 0x0F):
                self.skip_value()
                self.skip_value()
            return

        fixed_sizes = {
            0xCC: 1,
            0xCD: 2,
            0xCE: 4,
            0xCF: 8,
            0xD0: 1,
            0xD1: 2,
            0xD2: 4,
            0xD3: 8,
        }
        if prefix in fixed_sizes:
            self._skip_bytes(fixed_sizes[prefix])
            return

        if prefix == 0xC4:
            size = self._read_uint_be(1)
            self._skip_bytes(size)
            return
        if prefix == 0xC5:
            size = self._read_uint_be(2)
            self._skip_bytes(size)
            return
        if prefix == 0xC6:
            size = self._read_uint_be(4)
            self._skip_bytes(size)
            return
        if prefix == 0xD9:
            size = self._read_uint_be(1)
            self._skip_bytes(size)
            return
        if prefix == 0xDA:
            size = self._read_uint_be(2)
            self._skip_bytes(size)
            return
        if prefix == 0xDB:
            size = self._read_uint_be(4)
            self._skip_bytes(size)
            return
        if prefix == 0xDC:
            for _ in range(self._read_uint_be(2)):
                self.skip_value()
            return
        if prefix == 0xDD:
            for _ in range(self._read_uint_be(4)):
                self.skip_value()
            return
        if prefix == 0xDE:
            for _ in range(self._read_uint_be(2)):
                self.skip_value()
                self.skip_value()
            return
        if prefix == 0xDF:
            for _ in range(self._read_uint_be(4)):
                self.skip_value()
                self.skip_value()
            return
        raise ValueError(f"unsupported MessagePack prefix 0x{prefix:02x}")


def parse_binary_summary(data: bytes) -> BinaryAstSummary:
    reader = MessagePackReader(data)
    top_count = reader.read_map_len()
    format_name = ""
    schema_version = 0
    language = ""
    node_count = 0
    first_rule = ""
    rule_counts: dict[str, int] = {}

    for _ in range(top_count):
        key = reader.read_str()
        if key == "format":
            format_name = reader.read_str()
        elif key == "schemaVersion":
            schema_version = reader.read_uint()
        elif key == "language":
            language = reader.read_str()
        elif key == "nodeCount":
            node_count = reader.read_uint()
        elif key == "nodes":
            nodes_len = reader.read_array_len()
            node_count = nodes_len
            for _node_index in range(nodes_len):
                node_map_len = reader.read_map_len()
                node_rule = ""
                for _field_index in range(node_map_len):
                    node_key = reader.read_str()
                    if node_key == "rule":
                        node_rule = reader.read_str()
                    else:
                        reader.skip_value()
                if node_rule:
                    if not first_rule:
                        first_rule = node_rule
                    rule_counts[node_rule] = rule_counts.get(node_rule, 0) + 1
        else:
            reader.skip_value()

    if reader.pos != len(data):
        raise ValueError("MessagePack document has trailing bytes")
    if format_name != "tsmp-binary":
        raise ValueError(f"unexpected binary format: {format_name!r}")
    if schema_version != 1:
        raise ValueError(f"unsupported binary schema version: {schema_version}")

    return BinaryAstSummary(format_name, schema_version, language, node_count, first_rule, rule_counts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse Java inventory rows with FastParse binary output into SQLite."
    )
    parser.add_argument("--inventory-db", type=Path, default=DEFAULT_INVENTORY_DB)
    parser.add_argument("--out-db", type=Path, default=DEFAULT_OUTPUT_DB)
    parser.add_argument("--lib", type=Path, default=default_library_path())
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 12))
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-in-flight", type=int, default=0)
    parser.add_argument("--project", default="", help="Optional inventory project_name filter.")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--rules", default="", help="Pipe-separated Tree-sitter rules. Empty means all.")
    parser.add_argument("--fields", default="", help="Comma-separated fields. Empty means all fields.")
    parser.add_argument("--include-tokens", action="store_true")
    parser.add_argument(
        "--inspect-binary-metadata",
        action="store_true",
        help="Scan MessagePack nodes in Python to fill root_rule/rule_counts_json. Slower with threads.",
    )
    parser.add_argument("--progress-every", type=int, default=100)
    return parser.parse_args()


def connect_output_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA cache_size = -262144")
    return conn


def create_output_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS parse_runs (
            id INTEGER PRIMARY KEY,
            started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            inventory_db TEXT NOT NULL,
            library_path TEXT NOT NULL,
            library_version TEXT NOT NULL,
            workers INTEGER NOT NULL,
            fields TEXT NOT NULL,
            rules TEXT NOT NULL,
            include_tokens INTEGER NOT NULL,
            inspect_binary_metadata INTEGER NOT NULL DEFAULT 0,
            total_files INTEGER NOT NULL DEFAULT 0,
            parsed_files INTEGER NOT NULL DEFAULT 0,
            failed_files INTEGER NOT NULL DEFAULT 0,
            source_bytes INTEGER NOT NULL DEFAULT 0,
            ast_binary_bytes INTEGER NOT NULL DEFAULT 0,
            nodes INTEGER NOT NULL DEFAULT 0,
            elapsed_ms REAL NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS parsed_java_files (
            id INTEGER PRIMARY KEY,
            run_id INTEGER NOT NULL REFERENCES parse_runs(id) ON DELETE CASCADE,
            inventory_file_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            absolute_path TEXT NOT NULL,
            root_relative_path TEXT NOT NULL,
            project_relative_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            package_name TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            source_bytes INTEGER NOT NULL,
            line_count INTEGER NOT NULL,
            node_count INTEGER NOT NULL,
            ast_binary_bytes INTEGER NOT NULL,
            elapsed_ms REAL NOT NULL,
            schema_version INTEGER NOT NULL,
            language TEXT NOT NULL,
            root_rule TEXT NOT NULL,
            rule_counts_json TEXT NOT NULL,
            ast_binary BLOB NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(run_id, inventory_file_id)
        );

        CREATE TABLE IF NOT EXISTS parse_errors (
            id INTEGER PRIMARY KEY,
            run_id INTEGER NOT NULL REFERENCES parse_runs(id) ON DELETE CASCADE,
            inventory_file_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            absolute_path TEXT NOT NULL,
            elapsed_ms REAL NOT NULL,
            error TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_parsed_java_files_run_id
            ON parsed_java_files(run_id);
        CREATE INDEX IF NOT EXISTS idx_parsed_java_files_inventory_file_id
            ON parsed_java_files(inventory_file_id);
        CREATE INDEX IF NOT EXISTS idx_parsed_java_files_project_name
            ON parsed_java_files(project_name);
        CREATE INDEX IF NOT EXISTS idx_parsed_java_files_file_name
            ON parsed_java_files(file_name);
        CREATE INDEX IF NOT EXISTS idx_parsed_java_files_node_count
            ON parsed_java_files(node_count);
        CREATE INDEX IF NOT EXISTS idx_parse_errors_run_id
            ON parse_errors(run_id);
        """
    )
    columns = {
        str(row[1])
        for row in conn.execute("PRAGMA table_info(parse_runs)")
    }
    if "inspect_binary_metadata" not in columns:
        conn.execute(
            "ALTER TABLE parse_runs "
            "ADD COLUMN inspect_binary_metadata INTEGER NOT NULL DEFAULT 0"
        )


def load_work_items(db_path: Path, *, project: str, limit: int) -> list[WorkItem]:
    query = """
        SELECT
            id,
            project_id,
            project_name,
            absolute_path,
            root_relative_path,
            project_relative_path,
            file_name,
            package_name,
            size_bytes,
            line_count,
            sha256
        FROM java_files
    """
    params: list[Any] = []
    if project:
        query += " WHERE project_name = ?"
        params.append(project)
    query += " ORDER BY project_name, project_relative_path"
    if limit > 0:
        query += " LIMIT ?"
        params.append(limit)

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(query, params).fetchall()
    finally:
        conn.close()

    return [
        WorkItem(
            inventory_file_id=int(row[0]),
            project_id=int(row[1]),
            project_name=str(row[2]),
            absolute_path=str(row[3]),
            root_relative_path=str(row[4]),
            project_relative_path=str(row[5]),
            file_name=str(row[6]),
            package_name=str(row[7]),
            source_bytes=int(row[8]),
            line_count=int(row[9]),
            sha256=str(row[10]),
        )
        for row in rows
    ]


def init_worker(library_path: str) -> None:
    _THREAD_LOCAL.parser = FastParse(library_path)


def parse_one(
    item: WorkItem,
    output_format: str,
    rules: str,
    fields: int,
    include_tokens: bool,
    inspect_binary_metadata: bool,
) -> ParseSuccess | ParseFailure:
    started = time.perf_counter()
    try:
        parser = getattr(_THREAD_LOCAL, "parser", None)
        if parser is None:
            parser = FastParse()
            _THREAD_LOCAL.parser = parser

        source = Path(item.absolute_path).read_bytes()
        result = parser.parse_bytes(
            source,
            language="java",
            output_format=output_format,
            include_rules=rules,
            fields=fields,
            include_tokens=include_tokens,
            pretty=False,
        )
        if inspect_binary_metadata:
            summary = parse_binary_summary(result.data)
            if summary.node_count != result.node_count:
                raise ValueError(
                    f"binary nodeCount {summary.node_count} != native node_count {result.node_count}"
                )
        else:
            summary = BinaryAstSummary(
                "tsmp-binary",
                1,
                "java",
                result.node_count,
                "",
                {},
            )

        elapsed_ms = (time.perf_counter() - started) * 1000
        return ParseSuccess(
            item=item,
            ast_binary=result.data,
            node_count=result.node_count,
            binary_bytes=len(result.data),
            elapsed_ms=elapsed_ms,
            summary=summary,
        )
    except Exception as exc:  # noqa: BLE001 - file-level errors must be persisted.
        elapsed_ms = (time.perf_counter() - started) * 1000
        return ParseFailure(item=item, elapsed_ms=elapsed_ms, error=str(exc))


def create_run(
    conn: sqlite3.Connection,
    *,
    inventory_db: Path,
    library_path: Path,
    library_version: str,
    workers: int,
    fields: str,
    rules: str,
    include_tokens: bool,
    inspect_binary_metadata: bool,
    total_files: int,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO parse_runs(
            inventory_db,
            library_path,
            library_version,
            workers,
            fields,
            rules,
            include_tokens,
            inspect_binary_metadata,
            total_files
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(inventory_db),
            str(library_path),
            library_version,
            workers,
            fields,
            rules,
            1 if include_tokens else 0,
            1 if inspect_binary_metadata else 0,
            total_files,
        ),
    )
    conn.commit()
    return int(cursor.lastrowid)


def save_batch(
    conn: sqlite3.Connection,
    *,
    run_id: int,
    successes: list[ParseSuccess],
    failures: list[ParseFailure],
) -> None:
    with conn:
        conn.executemany(
            """
            INSERT INTO parsed_java_files(
                run_id,
                inventory_file_id,
                project_id,
                project_name,
                absolute_path,
                root_relative_path,
                project_relative_path,
                file_name,
                package_name,
                sha256,
                source_bytes,
                line_count,
                node_count,
                ast_binary_bytes,
                elapsed_ms,
                schema_version,
                language,
                root_rule,
                rule_counts_json,
                ast_binary
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    success.item.inventory_file_id,
                    success.item.project_id,
                    success.item.project_name,
                    success.item.absolute_path,
                    success.item.root_relative_path,
                    success.item.project_relative_path,
                    success.item.file_name,
                    success.item.package_name,
                    success.item.sha256,
                    success.item.source_bytes,
                    success.item.line_count,
                    success.node_count,
                    success.binary_bytes,
                    success.elapsed_ms,
                    success.summary.schema_version,
                    success.summary.language,
                    success.summary.first_rule,
                    json.dumps(
                        success.summary.rule_counts,
                        ensure_ascii=True,
                        separators=(",", ":"),
                        sort_keys=True,
                    ),
                    sqlite3.Binary(success.ast_binary),
                )
                for success in successes
            ],
        )
        conn.executemany(
            """
            INSERT INTO parse_errors(
                run_id,
                inventory_file_id,
                project_name,
                absolute_path,
                elapsed_ms,
                error
            )
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    failure.item.inventory_file_id,
                    failure.item.project_name,
                    failure.item.absolute_path,
                    failure.elapsed_ms,
                    failure.error,
                )
                for failure in failures
            ],
        )


def finalize_run(conn: sqlite3.Connection, *, run_id: int, elapsed_ms: float) -> None:
    conn.execute(
        """
        UPDATE parse_runs
        SET
            completed_at = CURRENT_TIMESTAMP,
            parsed_files = (
                SELECT COUNT(*)
                FROM parsed_java_files
                WHERE run_id = ?
            ),
            failed_files = (
                SELECT COUNT(*)
                FROM parse_errors
                WHERE run_id = ?
            ),
            source_bytes = (
                SELECT COALESCE(SUM(source_bytes), 0)
                FROM parsed_java_files
                WHERE run_id = ?
            ),
            ast_binary_bytes = (
                SELECT COALESCE(SUM(ast_binary_bytes), 0)
                FROM parsed_java_files
                WHERE run_id = ?
            ),
            nodes = (
                SELECT COALESCE(SUM(node_count), 0)
                FROM parsed_java_files
                WHERE run_id = ?
            ),
            elapsed_ms = ?
        WHERE id = ?
        """,
        (run_id, run_id, run_id, run_id, run_id, elapsed_ms, run_id),
    )
    conn.commit()


def submit_next(
    executor: ThreadPoolExecutor,
    iterator: Any,
    pending: dict[Any, WorkItem],
    *,
    output_format: str,
    rules: str,
    fields: int,
    include_tokens: bool,
    inspect_binary_metadata: bool,
) -> bool:
    try:
        item = next(iterator)
    except StopIteration:
        return False
    future = executor.submit(
        parse_one,
        item,
        output_format,
        rules,
        fields,
        include_tokens,
        inspect_binary_metadata,
    )
    pending[future] = item
    return True


def print_run_summary(conn: sqlite3.Connection, run_id: int) -> None:
    row = conn.execute(
        """
        SELECT
            library_version,
            workers,
            total_files,
            parsed_files,
            failed_files,
            source_bytes,
            ast_binary_bytes,
            nodes,
            elapsed_ms
        FROM parse_runs
        WHERE id = ?
        """,
        (run_id,),
    ).fetchone()
    if not row:
        return

    elapsed = float(row[8]) / 1000
    files_per_sec = float(row[3]) / elapsed if elapsed > 0 else 0
    nodes_per_sec = float(row[7]) / elapsed if elapsed > 0 else 0

    print(f"Run ID           : {run_id}")
    print(f"Library          : {row[0]}")
    print(f"Workers          : {row[1]}")
    print(f"Inventory files  : {row[2]}")
    print(f"Parsed OK        : {row[3]}")
    print(f"Errors           : {row[4]}")
    print(f"Source bytes     : {row[5]}")
    print(f"Binary AST bytes : {row[6]}")
    print(f"Nodes            : {row[7]}")
    print(f"Elapsed          : {elapsed:.3f}s")
    print(f"Files/sec        : {files_per_sec:.1f}")
    print(f"Nodes/sec        : {nodes_per_sec:.1f}")


def main() -> int:
    args = parse_args()
    inventory_db = args.inventory_db.resolve()
    output_db = args.out_db.resolve()
    library_path = args.lib.resolve()

    if not inventory_db.is_file():
        print(f"ERROR: inventory DB does not exist: {inventory_db}")
        return 2
    if not library_path.is_file():
        print(f"ERROR: FastParse library does not exist: {library_path}")
        return 2

    workers = max(1, args.workers)
    batch_size = max(1, args.batch_size)
    max_in_flight = args.max_in_flight if args.max_in_flight > 0 else workers * 2
    fields = parse_field_mask(args.fields)
    items = load_work_items(inventory_db, project=args.project, limit=args.limit)
    if not items:
        print("No Java files found in inventory for the selected filters.")
        return 2

    probe = FastParse(library_path)
    conn = connect_output_db(output_db)
    create_output_schema(conn)
    run_id = create_run(
        conn,
        inventory_db=inventory_db,
        library_path=library_path,
        library_version=probe.version,
        workers=workers,
        fields=args.fields or "(all)",
        rules=args.rules or "(all)",
        include_tokens=args.include_tokens,
        inspect_binary_metadata=args.inspect_binary_metadata,
        total_files=len(items),
    )

    started = time.perf_counter()
    parsed = 0
    failed = 0
    batch_successes: list[ParseSuccess] = []
    batch_failures: list[ParseFailure] = []
    iterator = iter(items)

    print(f"Inventory DB : {inventory_db}")
    print(f"Output DB    : {output_db}")
    print(f"Run ID       : {run_id}")
    print(f"Files        : {len(items)}")
    print(f"Workers      : {workers}")
    print(f"Max in flight: {max_in_flight}")

    try:
        with ThreadPoolExecutor(
            max_workers=workers,
            initializer=init_worker,
            initargs=(str(library_path),),
        ) as executor:
            pending: dict[Any, WorkItem] = {}
            while len(pending) < max_in_flight and submit_next(
                executor,
                iterator,
                pending,
                output_format="binary",
                rules=args.rules,
                fields=fields,
                include_tokens=args.include_tokens,
                inspect_binary_metadata=args.inspect_binary_metadata,
            ):
                pass

            while pending:
                done, _remaining = wait(pending, return_when=FIRST_COMPLETED)
                for future in done:
                    pending.pop(future)
                    result = future.result()
                    if isinstance(result, ParseSuccess):
                        batch_successes.append(result)
                        parsed += 1
                    else:
                        batch_failures.append(result)
                        failed += 1

                    if len(batch_successes) + len(batch_failures) >= batch_size:
                        save_batch(
                            conn,
                            run_id=run_id,
                            successes=batch_successes,
                            failures=batch_failures,
                        )
                        batch_successes.clear()
                        batch_failures.clear()

                    done_count = parsed + failed
                    if args.progress_every > 0 and done_count % args.progress_every == 0:
                        elapsed = time.perf_counter() - started
                        print(
                            f"Progress     : {done_count}/{len(items)} "
                            f"ok={parsed} errors={failed} elapsed={elapsed:.3f}s"
                        )

                    submit_next(
                        executor,
                        iterator,
                        pending,
                        output_format="binary",
                        rules=args.rules,
                        fields=fields,
                        include_tokens=args.include_tokens,
                        inspect_binary_metadata=args.inspect_binary_metadata,
                    )

        if batch_successes or batch_failures:
            save_batch(conn, run_id=run_id, successes=batch_successes, failures=batch_failures)

        elapsed_ms = (time.perf_counter() - started) * 1000
        finalize_run(conn, run_id=run_id, elapsed_ms=elapsed_ms)
        print_run_summary(conn, run_id)
        return 1 if failed else 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
