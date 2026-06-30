#!/usr/bin/env python3
"""Audit framework query captures against the shared parser lab inventory."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT.parents[1]
DEFAULT_DB = LAB_ROOT / "inventory" / "parser_lab_inventory.sqlite"
DEFAULT_SOURCE_ROOT = Path("/Users/natanbarronlugo/Desktop/Proyectos/mifel/fuentes/meta")
DEFAULT_QUERY = ROOT / "queries" / "frameworks.scm"
DEFAULT_JSON = ROOT / "audits" / "framework_query_family_audit.json"
DEFAULT_REPORT = ROOT / "audits" / "framework_query_family_audit.md"

CAPTURE_RE = re.compile(r"capture:\s+\d+\s+-\s+(?P<capture>[\w.]+),.*text:\s+`(?P<text>.*)`$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit tree-sitter framework query captures.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--query", type=Path, default=DEFAULT_QUERY)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--sample-limit", type=int, default=5)
    return parser.parse_args()


def inventory_paths(db_path: Path, source_root: Path) -> list[Path]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT f.absolute_path
            FROM files f
            JOIN source_roots sr ON f.source_root_id = sr.id
            WHERE sr.absolute_path = ?
              AND f.type = 'java'
              AND f.subtype = 'framework'
            ORDER BY f.absolute_path
            """,
            (source_root.as_posix(),),
        ).fetchall()
    finally:
        conn.close()
    return [Path(row[0]) for row in rows]


def run_tree_sitter_query(query_path: Path, source_path: Path) -> tuple[int, str, str]:
    result = subprocess.run(
        ["tree-sitter", "query", query_path.as_posix(), source_path.as_posix()],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
    )
    return result.returncode, result.stdout, result.stderr


def audit(paths: list[Path], query_path: Path, sample_limit: int) -> dict[str, object]:
    capture_counts: Counter[str] = Counter()
    capture_files: defaultdict[str, set[str]] = defaultdict(set)
    capture_samples: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    failed: list[dict[str, str]] = []
    files_with_any_capture = 0
    start = time.time()

    for index, path in enumerate(paths, 1):
        code, stdout, stderr = run_tree_sitter_query(query_path, path)
        if code != 0:
            failed.append({"path": path.as_posix(), "stderr": stderr.strip()})
        file_had_capture = False
        for line in stdout.splitlines():
            match = CAPTURE_RE.search(line)
            if not match:
                continue
            capture = match.group("capture")
            text = match.group("text")
            capture_counts[capture] += 1
            capture_files[capture].add(path.as_posix())
            file_had_capture = True
            if len(capture_samples[capture]) < sample_limit:
                capture_samples[capture].append({"path": path.as_posix(), "text": text})
        if file_had_capture:
            files_with_any_capture += 1
        if index % 500 == 0:
            print(f"progress {index}/{len(paths)} elapsed={time.time() - start:.1f}s", flush=True)

    captures = {
        capture: {
            "count": count,
            "files": len(capture_files[capture]),
            "samples": capture_samples[capture],
        }
        for capture, count in sorted(capture_counts.items(), key=lambda item: (-item[1], item[0]))
    }
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "grammar_root": ROOT.as_posix(),
        "query": query_path.as_posix(),
        "inventory_files": len(paths),
        "files_with_any_capture": files_with_any_capture,
        "query_failures": failed,
        "elapsed_seconds": round(time.time() - start, 2),
        "captures": captures,
    }


def family_summary(captures: dict[str, object]) -> list[tuple[str, int, int]]:
    family_counts: Counter[str] = Counter()
    family_files: defaultdict[str, set[str]] = defaultdict(set)
    for capture, payload_obj in captures.items():
        payload = payload_obj if isinstance(payload_obj, dict) else {}
        parts = capture.split(".")
        family = parts[1] if len(parts) >= 3 else "unknown"
        family_counts[family] += int(payload.get("count", 0))
        for sample in payload.get("samples", []):
            if isinstance(sample, dict) and "path" in sample:
                family_files[family].add(str(sample["path"]))
    return [(family, count, len(family_files[family])) for family, count in family_counts.most_common()]


def write_report(report_path: Path, result: dict[str, object]) -> None:
    captures = result["captures"]
    assert isinstance(captures, dict)
    failures = result["query_failures"]
    assert isinstance(failures, list)

    lines: list[str] = [
        "# Framework Query Family Audit",
        "",
        f"Date: {result['generated_at']}",
        "",
        "## Summary",
        "",
        f"- Inventory files: {result['inventory_files']}",
        f"- Files with any framework capture: {result['files_with_any_capture']}",
        f"- Query failures: {len(failures)}",
        f"- Elapsed seconds: {result['elapsed_seconds']}",
        "",
        "## Capture Counts",
        "",
        "| Capture | Count | Files |",
        "| --- | ---: | ---: |",
    ]
    for capture, payload_obj in captures.items():
        payload = payload_obj if isinstance(payload_obj, dict) else {}
        lines.append(f"| `{capture}` | {payload.get('count', 0)} | {payload.get('files', 0)} |")

    lines.extend(["", "## Samples", ""])
    for capture, payload_obj in captures.items():
        payload = payload_obj if isinstance(payload_obj, dict) else {}
        samples = payload.get("samples", [])
        if not samples:
            continue
        lines.extend([f"### `{capture}`", ""])
        for sample in samples:
            if not isinstance(sample, dict):
                continue
            lines.append(f"- `{sample.get('text', '')}`")
            lines.append(f"  Path: `{sample.get('path', '')}`")
        lines.append("")

    if failures:
        lines.extend(["## Query Failures", ""])
        for failure in failures[:20]:
            lines.append(f"- `{failure.get('path', '')}`: `{failure.get('stderr', '')}`")
        lines.append("")

    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    paths = inventory_paths(args.db, args.source_root.resolve())
    result = audit(paths, args.query.resolve(), args.sample_limit)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    write_report(args.report_out, result)
    print(f"inventory_files         : {result['inventory_files']}")
    print(f"files_with_any_capture : {result['files_with_any_capture']}")
    print(f"query_failures         : {len(result['query_failures'])}")
    print(f"json_out               : {args.json_out}")
    print(f"report_out             : {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
