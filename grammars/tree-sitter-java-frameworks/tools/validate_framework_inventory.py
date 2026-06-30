#!/usr/bin/env python3
"""Validate Java inventory files with encoding normalization and compact reports."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
import tempfile
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT.parents[1]
DEFAULT_DB = LAB_ROOT / "inventory" / "parser_lab_inventory.sqlite"
DEFAULT_JSON = ROOT / "audits" / "framework_inventory_validation.json"
DEFAULT_MSGPACK = ROOT / "audits" / "framework_inventory_validation.msgpack"
DEFAULT_REPORT = ROOT / "audits" / "framework_inventory_validation.md"
ERROR_RE = re.compile(r"\bERROR\b")
MISSING_RE = re.compile(r"\bMISSING\b")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate parser-lab Java inventory with threads and encoding normalization.",
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--source-root", type=Path, action="append")
    parser.add_argument("--subtype", action="append")
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--msgpack-out", type=Path, default=DEFAULT_MSGPACK)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--sample-limit", type=int, default=40)
    parser.add_argument("--no-msgpack", action="store_true")
    return parser.parse_args()


def inventory_paths(db_path: Path, source_roots: list[Path] | None, subtypes: list[str] | None) -> list[dict[str, str]]:
    query = [
        "SELECT f.absolute_path, sr.absolute_path, COALESCE(f.subtype, '')",
        "FROM files f JOIN source_roots sr ON f.source_root_id = sr.id",
        "WHERE f.type = 'java'",
    ]
    params: list[str] = []
    if source_roots:
        placeholders = ",".join("?" for _ in source_roots)
        query.append(f"AND sr.absolute_path IN ({placeholders})")
        params.extend(root.resolve().as_posix() for root in source_roots)
    if subtypes:
        placeholders = ",".join("?" for _ in subtypes)
        query.append(f"AND COALESCE(f.subtype, '') IN ({placeholders})")
        params.extend(subtypes)
    query.append("ORDER BY sr.absolute_path, f.subtype, f.absolute_path")

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("\n".join(query), params).fetchall()
    finally:
        conn.close()
    return [
        {"path": row[0], "source_root": row[1], "subtype": row[2]}
        for row in rows
    ]


def decode_source(path: Path) -> tuple[str, str, str, int, int, int]:
    data = path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            text = data.decode(encoding)
            return text, encoding, sha256, len(data), data.count(b"\n"), data.count(b"\r")
        except UnicodeDecodeError:
            continue
    text = data.decode("latin-1", errors="replace")
    return text, "latin-1-replace", sha256, len(data), data.count(b"\n"), data.count(b"\r")


def parse_one(item: dict[str, str]) -> dict[str, Any]:
    source_path = Path(item["path"])
    start = time.perf_counter()
    text, encoding, sha256, byte_size, lf_count, cr_count = decode_source(source_path)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    encoding_normalized = encoding != "utf-8"
    line_ending_normalized = normalized != text
    tmp_path: Path | None = None
    try:
        if not encoding_normalized and not line_ending_normalized:
            parse_path = source_path
            normalized_for_parse = False
        else:
            handle, tmp_name = tempfile.mkstemp(prefix="javafw_norm_", suffix=".java")
            tmp_path = Path(tmp_name)
            with open(handle, "w", encoding="utf-8") as tmp_file:
                tmp_file.write(normalized)
            parse_path = tmp_path
            normalized_for_parse = True

        result = subprocess.run(
            ["tree-sitter", "parse", "--quiet", parse_path.as_posix()],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
        )
        output = f"{result.stdout or ''}\n{result.stderr or ''}"
        error_nodes = len(ERROR_RE.findall(output))
        missing_nodes = len(MISSING_RE.findall(output))
        status = "ok"
        if result.returncode != 0:
            status = "hard_failure"
        if error_nodes:
            status = "error"
        if missing_nodes:
            status = "missing" if status == "ok" else f"{status}+missing"
        return {
            "path": item["path"],
            "source_root": item["source_root"],
            "subtype": item["subtype"],
            "byte_size": byte_size,
            "sha256": sha256,
            "original_encoding": encoding,
            "parser_input_encoding": "utf-8",
            "normalized_for_parse": normalized_for_parse,
            "encoding_normalized": encoding_normalized,
            "line_ending_normalized": line_ending_normalized,
            "lf_count": lf_count,
            "cr_count": cr_count,
            "line_count": normalized.count("\n") + (1 if normalized else 0),
            "returncode": result.returncode,
            "status": status,
            "error_nodes": error_nodes,
            "missing_nodes": missing_nodes,
            "duration_ms": round((time.perf_counter() - start) * 1000, 3),
            "diagnostic": (result.stderr or result.stdout or "").strip()[:1200],
        }
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


def msgpack_pack(value: Any) -> bytes:
    """Pack simple JSON-like data as MessagePack without an external dependency."""
    if value is None:
        return b"\xc0"
    if value is False:
        return b"\xc2"
    if value is True:
        return b"\xc3"
    if isinstance(value, int):
        if 0 <= value <= 0x7F:
            return bytes([value])
        if -32 <= value < 0:
            return bytes([0x100 + value])
        if 0 <= value <= 0xFF:
            return b"\xcc" + value.to_bytes(1, "big")
        if 0 <= value <= 0xFFFF:
            return b"\xcd" + value.to_bytes(2, "big")
        if 0 <= value <= 0xFFFFFFFF:
            return b"\xce" + value.to_bytes(4, "big")
        if value >= 0:
            return b"\xcf" + value.to_bytes(8, "big")
        if -0x80 <= value < 0:
            return b"\xd0" + value.to_bytes(1, "big", signed=True)
        if -0x8000 <= value < 0:
            return b"\xd1" + value.to_bytes(2, "big", signed=True)
        if -0x80000000 <= value < 0:
            return b"\xd2" + value.to_bytes(4, "big", signed=True)
        return b"\xd3" + value.to_bytes(8, "big", signed=True)
    if isinstance(value, float):
        import struct

        return b"\xcb" + struct.pack(">d", value)
    if isinstance(value, str):
        data = value.encode("utf-8")
        size = len(data)
        if size <= 31:
            return bytes([0xA0 | size]) + data
        if size <= 0xFF:
            return b"\xd9" + size.to_bytes(1, "big") + data
        if size <= 0xFFFF:
            return b"\xda" + size.to_bytes(2, "big") + data
        return b"\xdb" + size.to_bytes(4, "big") + data
    if isinstance(value, bytes):
        size = len(value)
        if size <= 0xFF:
            return b"\xc4" + size.to_bytes(1, "big") + value
        if size <= 0xFFFF:
            return b"\xc5" + size.to_bytes(2, "big") + value
        return b"\xc6" + size.to_bytes(4, "big") + value
    if isinstance(value, (list, tuple)):
        size = len(value)
        payload = b"".join(msgpack_pack(item) for item in value)
        if size <= 15:
            return bytes([0x90 | size]) + payload
        if size <= 0xFFFF:
            return b"\xdc" + size.to_bytes(2, "big") + payload
        return b"\xdd" + size.to_bytes(4, "big") + payload
    if isinstance(value, dict):
        items = list(value.items())
        size = len(items)
        payload = b"".join(msgpack_pack(str(key)) + msgpack_pack(val) for key, val in items)
        if size <= 15:
            return bytes([0x80 | size]) + payload
        if size <= 0xFFFF:
            return b"\xde" + size.to_bytes(2, "big") + payload
        return b"\xdf" + size.to_bytes(4, "big") + payload
    raise TypeError(f"unsupported MessagePack value: {type(value)!r}")


def summarize(results: list[dict[str, Any]], elapsed: float, args: argparse.Namespace) -> dict[str, Any]:
    encoding_counts = Counter(str(item["original_encoding"]) for item in results)
    by_root: defaultdict[str, Counter[str]] = defaultdict(Counter)
    issue_samples: list[dict[str, Any]] = []

    for item in results:
        key = f"{item['source_root']}|{item['subtype']}"
        bucket = by_root[key]
        bucket["files"] += 1
        bucket[f"encoding:{item['original_encoding']}"] += 1
        if item["normalized_for_parse"]:
            bucket["normalized"] += 1
        if item["encoding_normalized"]:
            bucket["encoding_normalized"] += 1
        if item["line_ending_normalized"]:
            bucket["line_ending_normalized"] += 1
        if item["returncode"] != 0:
            bucket["hard_failures"] += 1
        if item["error_nodes"]:
            bucket["files_with_error"] += 1
            bucket["error_nodes"] += int(item["error_nodes"])
        if item["missing_nodes"]:
            bucket["files_with_missing"] += 1
            bucket["missing_nodes"] += int(item["missing_nodes"])
        if (item["returncode"] != 0 or item["error_nodes"] or item["missing_nodes"]) and len(issue_samples) < args.sample_limit:
            issue_samples.append(item)

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "grammar_root": ROOT.as_posix(),
        "db": args.db.resolve().as_posix(),
        "source_roots": [root.resolve().as_posix() for root in args.source_root or []],
        "subtypes": args.subtype or [],
        "threads": args.threads,
        "inventory_files": len(results),
        "hard_failures": sum(1 for item in results if item["returncode"] != 0),
        "files_with_error": sum(1 for item in results if item["error_nodes"]),
        "total_error_nodes": sum(int(item["error_nodes"]) for item in results),
        "files_with_missing": sum(1 for item in results if item["missing_nodes"]),
        "total_missing_nodes": sum(int(item["missing_nodes"]) for item in results),
        "normalized_files": sum(1 for item in results if item["normalized_for_parse"]),
        "encoding_normalized_files": sum(1 for item in results if item["encoding_normalized"]),
        "line_ending_normalized_files": sum(1 for item in results if item["line_ending_normalized"]),
        "encoding_counts": dict(sorted(encoding_counts.items())),
        "elapsed_seconds": round(elapsed, 2),
        "by_root_subtype": {key: dict(counter) for key, counter in sorted(by_root.items())},
        "issue_samples": issue_samples,
    }
    return summary


def write_report(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Framework Inventory Validation",
        "",
        f"Date: {summary['generated_at']}",
        "",
        "## Summary",
        "",
        f"- Inventory files: {summary['inventory_files']}",
        f"- Threads: {summary['threads']}",
        f"- Hard failures: {summary['hard_failures']}",
        f"- Files with `ERROR`: {summary['files_with_error']}",
        f"- Total `ERROR` nodes: {summary['total_error_nodes']}",
        f"- Files with `MISSING`: {summary['files_with_missing']}",
        f"- Total `MISSING` nodes: {summary['total_missing_nodes']}",
        f"- Normalized files: {summary['normalized_files']}",
        f"- Encoding-normalized files: {summary['encoding_normalized_files']}",
        f"- Line-ending-normalized files: {summary['line_ending_normalized_files']}",
        f"- Elapsed seconds: {summary['elapsed_seconds']}",
        "",
        "## Encodings",
        "",
        "| Encoding | Files |",
        "| --- | ---: |",
    ]
    for encoding, count in summary["encoding_counts"].items():
        lines.append(f"| `{encoding}` | {count} |")

    lines.extend(["", "## By Root And Subtype", "", "| Root | Subtype | Files | Normalized | Encoding Norm | Line Ending Norm | Hard | Error Files | Error Nodes | Missing Files | Missing Nodes |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"])
    for key, payload in summary["by_root_subtype"].items():
        root, subtype = key.rsplit("|", 1)
        lines.append(
            f"| `{root}` | `{subtype}` | {payload.get('files', 0)} | {payload.get('normalized', 0)} | "
            f"{payload.get('encoding_normalized', 0)} | {payload.get('line_ending_normalized', 0)} | "
            f"{payload.get('hard_failures', 0)} | {payload.get('files_with_error', 0)} | {payload.get('error_nodes', 0)} | "
            f"{payload.get('files_with_missing', 0)} | {payload.get('missing_nodes', 0)} |"
        )

    samples = summary.get("issue_samples", [])
    if samples:
        lines.extend(["", "## Issue Samples", ""])
        for sample in samples:
            lines.append(
                f"- `{sample['path']}`: status={sample['status']} encoding={sample['original_encoding']} "
                f"errors={sample['error_nodes']} missing={sample['missing_nodes']}"
            )
            diagnostic = str(sample.get("diagnostic") or "").replace("\n", " ")
            if diagnostic:
                lines.append(f"  Diagnostic: `{diagnostic[:300]}`")
    else:
        lines.extend(["", "## Issue Samples", "", "No parse issues found."])

    lines.extend([
        "",
        "## Decision",
        "",
        "Stable if hard failures, `ERROR`, and `MISSING` counts are all zero.",
    ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    started = time.time()
    records = inventory_paths(args.db, args.source_root, args.subtype)
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(parse_one, item) for item in records]
        for index, future in enumerate(as_completed(futures), 1):
            results.append(future.result())
            if index % 500 == 0:
                print(f"progress {index}/{len(records)} elapsed={time.time() - started:.1f}s", flush=True)

    elapsed = time.time() - started
    results.sort(key=lambda item: (str(item["source_root"]), str(item["subtype"]), str(item["path"])))
    summary = summarize(results, elapsed, args)
    output = {"summary": summary, "results": results}

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    write_report(args.report_out, summary)
    if not args.no_msgpack:
        args.msgpack_out.parent.mkdir(parents=True, exist_ok=True)
        args.msgpack_out.write_bytes(msgpack_pack(output))

    print(f"inventory_files      : {summary['inventory_files']}")
    print(f"hard_failures        : {summary['hard_failures']}")
    print(f"files_with_error     : {summary['files_with_error']}")
    print(f"files_with_missing   : {summary['files_with_missing']}")
    print(f"normalized_files     : {summary['normalized_files']}")
    print(f"encoding_normalized  : {summary['encoding_normalized_files']}")
    print(f"line_ending_normalized: {summary['line_ending_normalized_files']}")
    print(f"json_out             : {args.json_out}")
    if not args.no_msgpack:
        print(f"msgpack_out          : {args.msgpack_out}")
    print(f"report_out           : {args.report_out}")
    return 0 if summary["hard_failures"] == 0 and summary["files_with_error"] == 0 and summary["files_with_missing"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
