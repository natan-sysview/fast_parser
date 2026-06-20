#!/usr/bin/env python3
"""Bulk parser probe for real Java projects.

This script is intentionally outside the C library's responsibilities:
Python walks directories, reads files, runs threads, and decides what to report.
The native library only receives in-memory bytes and returns in-memory bytes.
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from tsmp import Tsmp, default_library_path, parse_field_mask  # noqa: E402

DEFAULT_LIB = default_library_path()
DEFAULT_PROJECT = Path("/Users/natanbarronlugo/Desktop/Proyectos/javaswing/componentes")


@dataclass(frozen=True)
class FileResult:
    path: Path
    ok: bool
    source_bytes: int
    output_bytes: int
    nodes: int
    elapsed_ms: float
    error: str = ""


@dataclass(frozen=True)
class SourceItem:
    path: Path
    source: bytes | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse many Java files through FastParse.")
    parser.add_argument("project", nargs="?", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--lib", type=Path, default=DEFAULT_LIB)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--format", choices=("json", "csv", "stats", "binary", "msgpack"), default="json")
    parser.add_argument("--rules", default="class_declaration|interface_declaration|enum_declaration|method_declaration|constructor_declaration")
    parser.add_argument("--fields", default="id,parent_id,rule,range,child_count")
    parser.add_argument("--include-tokens", action="store_true")
    parser.add_argument("--preload", action="store_true", help="Read all source bytes before starting the timed parse.")
    parser.add_argument("--show-errors", type=int, default=10)
    return parser.parse_args()


def discover_java_files(root: Path, limit: int) -> list[Path]:
    files = sorted(path for path in root.rglob("*.java") if path.is_file())
    if limit > 0:
        return files[:limit]
    return files


def parse_file(
    tsmp: Tsmp,
    item: SourceItem,
    *,
    output_format: str,
    rules: str,
    fields: int,
    include_tokens: bool,
) -> FileResult:
    started = time.perf_counter()
    try:
        source = item.source if item.source is not None else item.path.read_bytes()
        result = tsmp.parse_bytes(
            source,
            language="java",
            output_format=output_format,
            include_rules=rules,
            fields=fields,
            include_tokens=include_tokens,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        return FileResult(item.path, True, len(source), len(result.data), result.node_count, elapsed_ms)
    except Exception as exc:  # noqa: BLE001 - probe should report all file-level failures.
        elapsed_ms = (time.perf_counter() - started) * 1000
        return FileResult(item.path, False, 0, 0, 0, elapsed_ms, str(exc))


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    files = discover_java_files(project, args.limit)
    fields = parse_field_mask(args.fields)

    if not files:
        print(f"No .java files found under {project}")
        return 2

    tsmp = Tsmp(args.lib.resolve())
    items = [
        SourceItem(path, path.read_bytes() if args.preload else None)
        for path in files
    ]
    started = time.perf_counter()
    results: list[FileResult] = []

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(
                parse_file,
                tsmp,
                item,
                output_format=args.format,
                rules=args.rules,
                fields=fields,
                include_tokens=args.include_tokens,
            )
            for item in items
        ]
        for future in as_completed(futures):
            results.append(future.result())

    total_elapsed = time.perf_counter() - started
    ok_results = [result for result in results if result.ok]
    error_results = [result for result in results if not result.ok]
    total_source = sum(result.source_bytes for result in ok_results)
    total_output = sum(result.output_bytes for result in ok_results)
    total_nodes = sum(result.nodes for result in ok_results)

    print(f"Library      : {tsmp.version}")
    print(f"Project      : {project}")
    print(f"Files        : {len(results)}")
    print(f"Parsed OK    : {len(ok_results)}")
    print(f"Errors       : {len(error_results)}")
    print(f"Workers      : {args.workers}")
    print(f"Preload      : {args.preload}")
    print(f"Format       : {args.format}")
    print(f"Rules        : {args.rules or '(all)'}")
    print(f"Fields       : {args.fields or '(all)'}")
    print(f"Source bytes : {total_source}")
    print(f"Output bytes : {total_output}")
    print(f"Nodes        : {total_nodes}")
    print(f"Elapsed      : {total_elapsed:.3f}s")
    print(f"Files/sec    : {len(results) / total_elapsed:.1f}")
    print(f"Nodes/sec    : {total_nodes / total_elapsed:.1f}")

    if error_results and args.show_errors > 0:
        print("Sample errors:")
        for result in error_results[: args.show_errors]:
            print(f"  {result.path}: {result.error}")

    return 1 if error_results else 0


if __name__ == "__main__":
    raise SystemExit(main())
