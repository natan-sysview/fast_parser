#!/usr/bin/env python3
"""Fast parse-quality scan using FastParse diagnostics output.

Diagnostics are useful when evaluating a grammar over a large corpus. The
native parser still parses the source, but returns a compact quality payload
instead of the full AST.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from fastparse import FastParse, OutputFormat, ParseOptions, default_library_path  # noqa: E402


@dataclass(frozen=True)
class ScanResult:
    path: Path
    ok: bool
    source_bytes: int
    source_lines: int
    elapsed_ms: float
    node_count: int
    has_errors: bool
    error_node_count: int
    missing_node_count: int
    error_byte_count: int
    error: str = ""


class WorkerContext(threading.local):
    parser: FastParse | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a threaded FastParse diagnostics scan.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--glob", default="*.java")
    parser.add_argument("--lib", type=Path, default=default_library_path())
    parser.add_argument("--language", default="java")
    parser.add_argument("--language-extension", type=Path)
    parser.add_argument("--normalization", default="auto_safe")
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out-db", type=Path, help="Optional SQLite file for diagnostics rows.")
    return parser.parse_args()


def count_lines(source: bytes) -> int:
    if not source:
        return 0
    return source.count(b"\n") + (0 if source.endswith(b"\n") else 1)


def discover(root: Path, pattern: str, limit: int) -> list[Path]:
    files = sorted(path for path in root.rglob(pattern) if path.is_file())
    return files[:limit] if limit > 0 else files


def parse_file(path: Path, args: argparse.Namespace, context: WorkerContext) -> ScanResult:
    started = time.perf_counter()
    source = b""
    try:
        if context.parser is None:
            context.parser = FastParse(args.lib)
            if args.language_extension and not context.parser.language_available(args.language):
                context.parser.load_language_extension(args.language_extension)

        source = path.read_bytes()
        result = context.parser.parse_bytes(
            source,
            ParseOptions(
                language=args.language,
                output_format=OutputFormat.DIAGNOSTICS,
                normalization=args.normalization,
            ),
        )
        payload = json.loads(result.data)
        return ScanResult(
            path=path,
            ok=True,
            source_bytes=len(source),
            source_lines=count_lines(source),
            elapsed_ms=(time.perf_counter() - started) * 1000.0,
            node_count=int(payload.get("nodeCount", result.node_count)),
            has_errors=bool(payload.get("hasErrors", False)),
            error_node_count=int(payload.get("errorNodeCount", 0)),
            missing_node_count=int(payload.get("missingNodeCount", 0)),
            error_byte_count=int(payload.get("errorByteCount", 0)),
        )
    except Exception as exc:  # noqa: BLE001 - corpus scan reports file-level failures.
        return ScanResult(
            path=path,
            ok=False,
            source_bytes=len(source),
            source_lines=count_lines(source),
            elapsed_ms=(time.perf_counter() - started) * 1000.0,
            node_count=0,
            has_errors=False,
            error_node_count=0,
            missing_node_count=0,
            error_byte_count=0,
            error=str(exc),
        )


def write_db(out_db: Path, results: list[ScanResult], root: Path, language: str) -> None:
    out_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(out_db) as conn:
        conn.executescript(
            """
            create table if not exists diagnostics (
                path text primary key,
                language text not null,
                ok integer not null,
                source_bytes integer not null,
                source_lines integer not null,
                elapsed_ms real not null,
                node_count integer not null,
                has_errors integer not null,
                error_node_count integer not null,
                missing_node_count integer not null,
                error_byte_count integer not null,
                error text not null
            );
            create index if not exists ix_diagnostics_errors on diagnostics(has_errors, error_node_count);
            """
        )
        conn.executemany(
            """
            insert or replace into diagnostics (
                path, language, ok, source_bytes, source_lines, elapsed_ms,
                node_count, has_errors, error_node_count, missing_node_count,
                error_byte_count, error
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    str(result.path.relative_to(root) if result.path.is_relative_to(root) else result.path),
                    language,
                    int(result.ok),
                    result.source_bytes,
                    result.source_lines,
                    result.elapsed_ms,
                    result.node_count,
                    int(result.has_errors),
                    result.error_node_count,
                    result.missing_node_count,
                    result.error_byte_count,
                    result.error,
                )
                for result in results
            ],
        )


def main() -> int:
    args = parse_args()
    files = discover(args.root, args.glob, args.limit)
    if not files:
        print(f"No files matched {args.glob} under {args.root}")
        return 2

    if args.language_extension:
        bootstrap = FastParse(args.lib)
        if not bootstrap.language_available(args.language):
            bootstrap.load_language_extension(args.language_extension)

    started = time.perf_counter()
    results: list[ScanResult] = []
    context = WorkerContext()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(parse_file, path, args, context) for path in files]
        for future in as_completed(futures):
            results.append(future.result())
    elapsed = time.perf_counter() - started

    ok = [result for result in results if result.ok]
    failed = [result for result in results if not result.ok]
    with_errors = [result for result in ok if result.has_errors]
    total_lines = sum(result.source_lines for result in ok)
    total_nodes = sum(result.node_count for result in ok)
    total_error_nodes = sum(result.error_node_count for result in ok)

    if args.out_db:
        write_db(args.out_db, results, args.root.resolve(), args.language)

    print(f"Root         : {args.root}")
    print(f"Language     : {args.language}")
    print(f"Workers      : {args.workers}")
    print(f"Files        : {len(results)}")
    print(f"Parsed OK    : {len(ok)}")
    print(f"Failed       : {len(failed)}")
    print(f"With errors  : {len(with_errors)}")
    print(f"Lines        : {total_lines}")
    print(f"Nodes        : {total_nodes}")
    print(f"Error nodes  : {total_error_nodes}")
    print(f"Elapsed      : {elapsed:.3f}s")
    print(f"Avg/file     : {(elapsed / len(results) * 1000.0):.3f} ms")
    print(f"Files/sec    : {(len(results) / elapsed):.1f}")
    print(f"Lines/sec    : {(total_lines / elapsed):.1f}")
    if args.out_db:
        print(f"Output DB    : {args.out_db}")

    for result in failed[:10]:
        print(f"ERROR {result.path}: {result.error}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
