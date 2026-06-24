#!/usr/bin/env python3
"""Decode FastParse binary MessagePack into Python dataclasses."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from fastparse import FastParse, Field, OutputFormat, ParseOptions  # noqa: E402


def main() -> int:
    parser = FastParse()
    result = parser.parse_bytes(
        b"class Demo { void run() { System.out.println(\"fastparse\"); } }",
        ParseOptions(
            output_format=OutputFormat.BINARY,
            include_rules=["class_declaration", "method_declaration"],
            fields=Field.ID | Field.PARENT_ID | Field.RULE | Field.TEXT | Field.BYTE_RANGE,
        ),
    )
    document = result.binary_document()

    print(f"Library : {parser.version}")
    print(f"Format  : {document.format} v{document.schema_version}")
    print(f"Language: {document.language}")
    print(f"Nodes   : {document.node_count}")
    for node in document.nodes:
        text = (node.text or b"").decode("utf-8", errors="replace").replace("\n", "\\n")
        print(f"  {node.id}: {node.rule} [{node.start_byte}, {node.end_byte}] {text}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
