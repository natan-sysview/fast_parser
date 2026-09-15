#!/usr/bin/env python3
"""Validate a built FastParse Maven jar contains Java classes and native resources."""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ALL_RIDS = ["linux-x64", "macos-x64", "macos-arm64", "windows-x64"]


def core_name(rid: str) -> str:
    if rid.startswith("windows"):
        return "fastparse.dll"
    if rid.startswith("macos"):
        return "libfastparse.dylib"
    return "libfastparse.so"


def jni_name(rid: str) -> str:
    if rid.startswith("windows"):
        return "fastparse_jni.dll"
    if rid.startswith("macos"):
        return "libfastparse_jni.dylib"
    return "libfastparse_jni.so"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate FastParse Maven jar layout.")
    parser.add_argument("jar", type=Path)
    parser.add_argument("--require-all-rids", action="store_true")
    parser.add_argument("--require-rid", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    required_rids = ALL_RIDS if args.require_all_rids or not args.require_rid else args.require_rid
    with zipfile.ZipFile(args.jar) as zf:
        names = set(zf.namelist())
    required = [
        "dev/fastparse/FastParseClient.class",
        "dev/fastparse/NativeBridge.class",
        "dev/fastparse/NativeLibraryLoader.class",
        "dev/fastparse/ParseOptions.class",
        "dev/fastparse/QueryOptions.class",
    ]
    for target_rid in required_rids:
        required.append(f"dev/fastparse/native/{target_rid}/{core_name(target_rid)}")
        required.append(f"dev/fastparse/native/{target_rid}/{jni_name(target_rid)}")
    missing = [name for name in required if name not in names]
    if missing:
        raise SystemExit("Missing Maven jar entries:\n" + "\n".join(missing))
    print(f"Maven jar validation passed: {args.jar}")
    print(f"Validated RIDs: {', '.join(required_rids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
