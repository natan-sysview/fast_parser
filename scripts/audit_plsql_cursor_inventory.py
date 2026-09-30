#!/usr/bin/env python3
"""Compare cursor structure and diagnostics across a PL/SQL inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from fastparse import FastParse, OutputFormat  # noqa: E402


RULES = (
    "cursor_definition",
    "legacy_cursor_definition_blob",
    "legacy_package_spec_cursor_definition_blob",
    "legacy_package_spec_cursor_select_blob",
    "ref_call",
    "with_clause",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--extension", type=Path, required=True)
    parser.add_argument("--core", type=Path, default=ROOT / "bin" / "libfastparse.dylib")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=8)
    return parser.parse_args()


def normalized_source(raw: bytes) -> tuple[bytes, str]:
    for encoding in ("utf-8", "cp1252", "iso-8859-1"):
        try:
            return raw.decode(encoding).encode("utf-8").rstrip(b" \t"), encoding
        except UnicodeDecodeError:
            continue
    raise AssertionError("iso-8859-1 must decode every byte sequence")


def audit_file(item: tuple, parser: FastParse) -> dict:
    file_id, path, subtype, expected_sha256 = item
    result = {"id": file_id, "path": path, "subtype": subtype}
    try:
        raw = Path(path).read_bytes()
        source, encoding = normalized_source(raw)
        document = parser.parse_bytes(
            source,
            language="plsql",
            output_format=OutputFormat.BINARY,
            include_rules=RULES,
            fields=["rule", "range", "byte_range", "diagnostics"],
        ).binary_document()
        counts = Counter(node.rule for node in document.nodes)
        result.update(
            encoding=encoding,
            sha256_matches_inventory=hashlib.sha256(raw).hexdigest() == expected_sha256,
            has_errors=bool(document.has_errors),
            error_nodes=document.error_node_count or 0,
            missing_nodes=document.missing_node_count or 0,
            error_bytes=document.error_byte_count or 0,
            counts={rule: counts[rule] for rule in RULES if counts[rule]},
        )
    except Exception as exc:  # Preserve failed files in the report.
        result["failure"] = f"{type(exc).__name__}: {exc}"
    return result


def main() -> int:
    args = parse_args()
    with sqlite3.connect(args.inventory) as connection:
        files = connection.execute(
            "SELECT id, absolute_path, subtype, sha256 FROM files "
            "WHERE type = 'plsql' ORDER BY id"
        ).fetchall()

    parser = FastParse(args.core)
    parser.load_language_extension(args.extension)
    start = time.monotonic()
    rows = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(audit_file, item, parser) for item in files]
        for future in as_completed(futures):
            rows.append(future.result())
            if len(rows) % 1000 == 0:
                print(f"Audited {len(rows)}/{len(files)}", flush=True)
    rows.sort(key=lambda row: row["id"])

    totals = Counter()
    encodings = Counter()
    for row in rows:
        if "failure" in row:
            totals["failures"] += 1
            continue
        encodings[row["encoding"]] += 1
        totals["files_with_errors"] += bool(row["has_errors"])
        totals["files_with_missing"] += row["missing_nodes"] > 0
        totals["error_nodes"] += row["error_nodes"]
        totals["missing_nodes"] += row["missing_nodes"]
        totals["error_bytes"] += row["error_bytes"]
        totals["hash_mismatches"] += not row["sha256_matches_inventory"]
        for rule, count in row["counts"].items():
            totals[rule] += count
            totals[f"files_with_{rule}"] += count > 0

    report = {
        "inventory": str(args.inventory.resolve()),
        "extension": str(args.extension.resolve()),
        "extension_sha256": hashlib.sha256(args.extension.read_bytes()).hexdigest(),
        "files": len(files),
        "threads": args.threads,
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "encodings": dict(encodings),
        "totals": dict(totals),
        "results": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: report[key] for key in ("files", "elapsed_seconds", "encodings", "totals")}, indent=2))
    return int(totals["failures"] > 0)


if __name__ == "__main__":
    raise SystemExit(main())
