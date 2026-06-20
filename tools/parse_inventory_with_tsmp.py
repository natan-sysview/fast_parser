#!/usr/bin/env python3
"""Parse Java files listed in the inventory DB through TSMP."""

from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from tsmp import Tsmp, default_library_path, parse_field_mask  # noqa: E402


DEFAULT_DB = ROOT / "data" / "java_swing_inventory.sqlite"


@dataclass(frozen=True)
class WorkItem:
    id: int
    project_name: str
    path: Path
    source: bytes | None = None


@dataclass(frozen=True)
class ParseFileResult:
    id: int
    project_name: str
    path: Path
    ok: bool
    source_bytes: int
    output_bytes: int
    nodes: int
    elapsed_ms: float
    error: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse Java files from the SQLite inventory using TSMP."
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--lib", type=Path, default=default_library_path())
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--format", choices=("json", "csv", "stats", "binary", "msgpack"), default="json")
    parser.add_argument("--rules", default="", help="Pipe-separated rules. Empty means all rules.")
    parser.add_argument("--fields", default="", help="Comma-separated fields. Empty means all fields.")
    parser.add_argument("--project", default="", help="Optional project_name filter.")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--include-tokens", action="store_true")
    parser.add_argument("--preload", action="store_true", help="Read all source bytes before timed parsing.")
    parser.add_argument("--copy-output", action="store_true", help="Copy output bytes into Python instead of discarding them.")
    parser.add_argument("--show-errors", type=int, default=10)
    return parser.parse_args()


def load_items(db_path: Path, *, project: str, limit: int, preload: bool) -> list[WorkItem]:
    query = """
        SELECT id, project_name, absolute_path
        FROM java_files
    """
    params: list[object] = []

    if project:
        query += " WHERE project_name = ?"
        params.append(project)

    query += " ORDER BY project_name, project_relative_path"

    if limit > 0:
        query += " LIMIT ?"
        params.append(limit)

    conn = sqlite3.connect(db_path)
    try:
        rows = list(conn.execute(query, params))
    finally:
        conn.close()

    items: list[WorkItem] = []
    for file_id, project_name, absolute_path in rows:
        path = Path(absolute_path)
        items.append(
            WorkItem(
                int(file_id),
                str(project_name),
                path,
                path.read_bytes() if preload else None,
            )
        )
    return items


def parse_one(
    tsmp: Tsmp,
    item: WorkItem,
    *,
    output_format: str,
    rules: str,
    fields: int,
    include_tokens: bool,
    copy_output: bool,
) -> ParseFileResult:
    started = time.perf_counter()
    try:
        source = item.source if item.source is not None else item.path.read_bytes()
        if copy_output:
            result = tsmp.parse_bytes(
                source,
                language="java",
                output_format=output_format,
                include_rules=rules,
                fields=fields,
                include_tokens=include_tokens,
            )
            output_bytes = len(result.data)
            nodes = result.node_count
        else:
            summary = tsmp.parse_bytes_summary(
                source,
                language="java",
                output_format=output_format,
                include_rules=rules,
                fields=fields,
                include_tokens=include_tokens,
            )
            output_bytes = summary.output_length
            nodes = summary.node_count

        elapsed_ms = (time.perf_counter() - started) * 1000
        return ParseFileResult(
            item.id,
            item.project_name,
            item.path,
            True,
            len(source),
            output_bytes,
            nodes,
            elapsed_ms,
        )
    except Exception as exc:  # noqa: BLE001 - runner should report file-level failures.
        elapsed_ms = (time.perf_counter() - started) * 1000
        return ParseFileResult(
            item.id,
            item.project_name,
            item.path,
            False,
            0,
            0,
            0,
            elapsed_ms,
            str(exc),
        )


def print_project_summary(results: list[ParseFileResult]) -> None:
    by_project: dict[str, list[ParseFileResult]] = {}
    for result in results:
        by_project.setdefault(result.project_name, []).append(result)

    print("Projects:")
    for project_name in sorted(by_project):
        project_results = by_project[project_name]
        ok_results = [result for result in project_results if result.ok]
        print(
            f"  {project_name:<58} "
            f"{len(ok_results):>5}/{len(project_results):<5} files "
            f"{sum(result.nodes for result in ok_results):>10} nodes "
            f"{sum(result.output_bytes for result in ok_results):>12} output bytes"
        )


def main() -> int:
    args = parse_args()
    db_path = args.db.resolve()

    if not db_path.is_file():
        print(f"ERROR: inventory DB does not exist: {db_path}")
        return 2

    fields = parse_field_mask(args.fields)
    items = load_items(db_path, project=args.project, limit=args.limit, preload=args.preload)
    if not items:
        print("No Java files found in inventory for the selected filters.")
        return 2

    tsmp = Tsmp(args.lib.resolve())
    started = time.perf_counter()
    results: list[ParseFileResult] = []

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(
                parse_one,
                tsmp,
                item,
                output_format=args.format,
                rules=args.rules,
                fields=fields,
                include_tokens=args.include_tokens,
                copy_output=args.copy_output,
            )
            for item in items
        ]
        for future in as_completed(futures):
            results.append(future.result())

    elapsed = time.perf_counter() - started
    ok_results = [result for result in results if result.ok]
    error_results = [result for result in results if not result.ok]
    total_source = sum(result.source_bytes for result in ok_results)
    total_output = sum(result.output_bytes for result in ok_results)
    total_nodes = sum(result.nodes for result in ok_results)

    print(f"Library      : {tsmp.version}")
    print(f"DB           : {db_path}")
    print(f"Files        : {len(results)}")
    print(f"Parsed OK    : {len(ok_results)}")
    print(f"Errors       : {len(error_results)}")
    print(f"Workers      : {args.workers}")
    print(f"Preload      : {args.preload}")
    print(f"Copy output  : {args.copy_output}")
    print(f"Format       : {args.format}")
    print(f"Rules        : {args.rules or '(all)'}")
    print(f"Fields       : {args.fields or '(all)'}")
    print(f"Source bytes : {total_source}")
    print(f"Output bytes : {total_output}")
    print(f"Nodes        : {total_nodes}")
    print(f"Elapsed      : {elapsed:.3f}s")
    print(f"Files/sec    : {len(results) / elapsed:.1f}")
    print(f"Nodes/sec    : {total_nodes / elapsed:.1f}")
    print_project_summary(results)

    if error_results and args.show_errors > 0:
        print("Sample errors:")
        for result in error_results[: args.show_errors]:
            print(f"  {result.path}: {result.error}")

    return 1 if error_results else 0


if __name__ == "__main__":
    raise SystemExit(main())
