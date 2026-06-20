#!/usr/bin/env python3
"""Benchmark TSMP formats against the SQLite Java inventory."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from tsmp import Tsmp, default_library_path, parse_field_mask  # noqa: E402


DEFAULT_DB = ROOT / "data" / "java_swing_inventory.sqlite"
DEFAULT_OUT = ROOT / "data" / "tsmp_benchmark_results.json"


@dataclass(frozen=True)
class Scenario:
    name: str
    output_format: str
    rules: str
    fields: str
    copy_output: bool = False


@dataclass(frozen=True)
class WorkItem:
    id: int
    path: Path
    source: bytes | None = None


@dataclass(frozen=True)
class BenchmarkResult:
    scenario: str
    output_format: str
    workers: int
    files: int
    parsed_ok: int
    errors: int
    source_bytes: int
    output_bytes: int
    nodes: int
    elapsed_s: float
    files_per_s: float
    nodes_per_s: float
    output_mb_per_s: float
    rules: str
    fields: str
    copy_output: bool


DEFAULT_SCENARIOS = [
    Scenario("stats_all", "stats", "", ""),
    Scenario("json_all", "json", "", ""),
    Scenario("binary_all", "binary", "", ""),
    Scenario("json_structural", "json", "", "id,parent_id,rule,range,byte_range"),
    Scenario("binary_structural", "binary", "", "id,parent_id,rule,range,byte_range"),
    Scenario(
        "csv_declarations",
        "csv",
        "class_declaration|interface_declaration|enum_declaration|method_declaration|constructor_declaration",
        "id,parent_id,rule,range,byte_range",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark TSMP output formats.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--lib", type=Path, default=default_library_path())
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--workers", default="1,4,8,12", help="Comma-separated worker counts.")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--project", default="")
    parser.add_argument("--preload", action="store_true")
    parser.add_argument(
        "--scenario",
        action="append",
        choices=[scenario.name for scenario in DEFAULT_SCENARIOS],
        help="Scenario to run. Repeatable. Default runs all scenarios.",
    )
    return parser.parse_args()


def parse_workers(raw: str) -> list[int]:
    workers = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        value = int(part)
        if value <= 0:
            raise ValueError("workers must be positive")
        workers.append(value)
    return workers or [1]


def load_items(db_path: Path, *, project: str, limit: int, preload: bool) -> list[WorkItem]:
    query = "SELECT id, absolute_path FROM java_files"
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

    return [
        WorkItem(int(file_id), Path(path), Path(path).read_bytes() if preload else None)
        for file_id, path in rows
    ]


def parse_one(
    tsmp: Tsmp,
    item: WorkItem,
    *,
    scenario: Scenario,
    fields: int,
) -> tuple[bool, int, int, int]:
    try:
        source = item.source if item.source is not None else item.path.read_bytes()
        if scenario.copy_output:
            result = tsmp.parse_bytes(
                source,
                language="java",
                output_format=scenario.output_format,
                include_rules=scenario.rules,
                fields=fields,
            )
            return True, len(source), len(result.data), result.node_count

        summary = tsmp.parse_bytes_summary(
            source,
            language="java",
            output_format=scenario.output_format,
            include_rules=scenario.rules,
            fields=fields,
        )
        return True, len(source), summary.output_length, summary.node_count
    except Exception:
        return False, 0, 0, 0


def run_scenario(tsmp: Tsmp, items: list[WorkItem], scenario: Scenario, workers: int) -> BenchmarkResult:
    fields = parse_field_mask(scenario.fields)
    started = time.perf_counter()
    ok = 0
    errors = 0
    source_bytes = 0
    output_bytes = 0
    nodes = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(parse_one, tsmp, item, scenario=scenario, fields=fields)
            for item in items
        ]
        for future in as_completed(futures):
            parsed, source_len, output_len, node_count = future.result()
            if parsed:
                ok += 1
                source_bytes += source_len
                output_bytes += output_len
                nodes += node_count
            else:
                errors += 1

    elapsed = time.perf_counter() - started
    return BenchmarkResult(
        scenario=scenario.name,
        output_format=scenario.output_format,
        workers=workers,
        files=len(items),
        parsed_ok=ok,
        errors=errors,
        source_bytes=source_bytes,
        output_bytes=output_bytes,
        nodes=nodes,
        elapsed_s=elapsed,
        files_per_s=len(items) / elapsed if elapsed else 0.0,
        nodes_per_s=nodes / elapsed if elapsed else 0.0,
        output_mb_per_s=(output_bytes / 1_000_000) / elapsed if elapsed else 0.0,
        rules=scenario.rules or "(all)",
        fields=scenario.fields or "(all)",
        copy_output=scenario.copy_output,
    )


def print_result(result: BenchmarkResult) -> None:
    print(
        f"{result.scenario:<18} "
        f"workers={result.workers:<2} "
        f"files={result.parsed_ok:>4}/{result.files:<4} "
        f"errors={result.errors:<2} "
        f"elapsed={result.elapsed_s:>7.3f}s "
        f"files/s={result.files_per_s:>8.1f} "
        f"nodes/s={result.nodes_per_s:>10.1f} "
        f"outMB={result.output_bytes / 1_000_000:>8.1f}"
    )


def main() -> int:
    args = parse_args()
    db_path = args.db.resolve()
    if not db_path.is_file():
        print(f"ERROR: inventory DB does not exist: {db_path}")
        return 2

    workers = parse_workers(args.workers)
    selected_names = set(args.scenario or [])
    scenarios = [
        scenario
        for scenario in DEFAULT_SCENARIOS
        if not selected_names or scenario.name in selected_names
    ]
    items = load_items(db_path, project=args.project, limit=args.limit, preload=args.preload)
    if not items:
        print("No Java files found in inventory for selected filters.")
        return 2

    tsmp = Tsmp(args.lib.resolve())
    results: list[BenchmarkResult] = []

    print(f"Library : {tsmp.version}")
    print(f"DB      : {db_path}")
    print(f"Files   : {len(items)}")
    print(f"Workers : {', '.join(str(value) for value in workers)}")
    print(f"Preload : {args.preload}")

    for scenario in scenarios:
        for worker_count in workers:
            result = run_scenario(tsmp, items, scenario, worker_count)
            results.append(result)
            print_result(result)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "library": tsmp.version,
        "db": str(db_path),
        "files": len(items),
        "preload": args.preload,
        "results": [asdict(result) for result in results],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved  : {args.out}")

    return 1 if any(result.errors for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
