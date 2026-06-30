#!/usr/bin/env python3
"""Run a Tree-sitter query over Java source with FastParse."""

from __future__ import annotations

from fastparse import FastParse, Field, OutputFormat, QueryOptions


SOURCE = """
public class Demo {
    public void run() {
        System.out.println("query");
    }
}
"""

QUERY = """
(method_declaration
  name: (identifier) @method.name) @method
"""


def main() -> None:
    parser = FastParse()
    result = parser.query_text(
        SOURCE,
        QUERY,
        QueryOptions(
            language="java",
            output_format=OutputFormat.JSON,
            fields=Field.CAPTURE_NAME | Field.RULE | Field.TEXT | Field.RANGE | Field.BYTE_RANGE,
        ),
    )
    print(f"Captures: {result.node_count}")
    print(result.text)


if __name__ == "__main__":
    main()
