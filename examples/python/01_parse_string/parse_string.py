#!/usr/bin/env python3
"""Small ctypes probe for the FastParse native library.

The Python side owns all file I/O. The C library receives source bytes already
in RAM and returns a JSON buffer that Python can print, inspect, or persist.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from tsmp import Tsmp, default_library_path, parse_field_mask  # noqa: E402

DEFAULT_SOURCE = ROOT / "file_test" / "java" / "HelloWorld.java"
INLINE_SOURCE = b"class Demo { void run() { System.out.println(\"fastparse\"); } }"
DEFAULT_LIB = default_library_path()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse Java source through the FastParse native library."
    )
    parser.add_argument("--lib", type=Path, default=DEFAULT_LIB)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--lang", default="java")
    parser.add_argument("--format", choices=("json", "csv", "stats", "binary", "msgpack"), default="json")
    parser.add_argument("--rules", default="", help='Pipe-separated rules, e.g. "class_declaration|method_declaration".')
    parser.add_argument("--fields", default="", help="Comma-separated fields. Empty means all.")
    parser.add_argument("--include-tokens", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--workers", type=int, default=1, help="Run N parallel parses of the same in-memory source.")
    return parser.parse_args()


def default_source() -> bytes:
    if DEFAULT_SOURCE.exists():
        return DEFAULT_SOURCE.read_bytes()
    return INLINE_SOURCE


def main() -> int:
    args = parse_args()
    source = args.source.resolve().read_bytes() if args.source else default_source()
    tsmp = Tsmp(args.lib.resolve())
    fields = parse_field_mask(args.fields)

    def parse_once() -> tuple[bytes, int]:
        result = tsmp.parse_bytes(
            source,
            language=args.lang,
            output_format=args.format,
            include_rules=args.rules,
            fields=fields,
            include_tokens=args.include_tokens,
            pretty=args.pretty,
        )
        return result.data, result.node_count

    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(lambda _: parse_once(), range(args.workers)))
        print(f"Library : {tsmp.version}")
        print(f"Workers : {args.workers}")
        print(f"Bytes   : {', '.join(str(len(output)) for output, _nodes in results)}")
        print(f"Nodes   : {', '.join(str(nodes) for _output, nodes in results)}")
        return 0

    output, node_count = parse_once()

    if args.summary and args.format == "stats":
        print(f"Library : {tsmp.version}")
        print(f"Language: {args.lang}")
        print(f"Nodes   : {node_count}")
        return 0

    if args.summary and args.format in ("binary", "msgpack"):
        print(f"Library : {tsmp.version}")
        print(f"Language: {args.lang}")
        print(f"Nodes   : {node_count}")
        print(f"Bytes   : {len(output)}")
        return 0

    if args.summary and args.format == "json":
        document = json.loads(output)
        print(f"Library : {tsmp.version}")
        print(f"Language: {document.get('language')}")
        print(f"Nodes   : {document.get('nodeCount')}")
        for node in document.get("nodes", [])[:12]:
            print(
                f"  {node.get('rule', ''):<28} "
                f"{node.get('startLine')}:{node.get('startColumn')}"
            )
        return 0

    if args.pretty and args.format == "json":
        document = json.loads(output)
        print(json.dumps(document, indent=2, ensure_ascii=False))
        return 0

    if args.format in ("binary", "msgpack"):
        sys.stdout.buffer.write(output)
        return 0

    print(output.decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
