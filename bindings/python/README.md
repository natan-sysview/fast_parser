# FastParse Python Binding

Small `ctypes` binding for the FastParse native C library.

The binding keeps the same design boundary as the native library:

- Python owns file I/O.
- Python passes bytes already loaded in RAM.
- FastParse returns JSON, CSV, MessagePack binary, diagnostics, or stats in RAM.
- FastParse can execute Tree-sitter queries and return matches/captures in RAM.
- Python copies the returned native buffer and frees the native result.

## Install

From PyPI, once the package is published:

```bash
pip install --pre fastparse
```

From a downloaded wheel:

```bash
pip install fastparse-0.1.0rc17-py3-none-macosx_11_0_arm64.whl
```

The wheel includes the native library for its platform and `py.typed` markers for type-aware tooling, so normal users do not need `FASTPARSE_LIBRARY_PATH`.

## Quick Use

```python
from fastparse import FastParse, Field, OutputFormat, ParseOptions

parser = FastParse()
source = b"class Demo { void run() {} }"

result = parser.parse_bytes(
    source,
    ParseOptions(
        language="java",
        output_format=OutputFormat.JSON,
        fields=Field.RULE | Field.TEXT | Field.BYTE_RANGE,
    ),
)

print(result.node_count)
print(result.json())
```

Tree-sitter query output:

```python
from fastparse import QueryOptions

query_result = parser.query_text(
    "class Demo { void run() {} }",
    "(method_declaration name: (identifier) @method.name) @method",
    QueryOptions(
        language="java",
        output_format=OutputFormat.JSON,
        fields=Field.CAPTURE_NAME | Field.RULE | Field.TEXT | Field.RANGE | Field.BYTE_RANGE,
    ),
)

print(query_result.json())
```

Binary MessagePack output:

```python
result = parser.parse_bytes(
    source,
    language="java",
    output_format="binary",
    fields=["rule", "text", "byte_range"],
)

print(result.node_count)
print(result.data)  # MessagePack bytes
```

Decode binary output into Python dataclasses:

```python
document = result.binary_document()
print(document.nodes[0].rule)
print(document.nodes[0].text)
```

If the caller only needs node/output counts and does not need to copy the generated JSON/CSV into Python:

```python
summary = parser.parse_bytes_summary(
    source,
    language="java",
    output_format="json",
)

print(summary.node_count)
print(summary.output_length)
```

Use `FASTPARSE_LIBRARY_PATH` to point at a specific native library:

```bash
FASTPARSE_LIBRARY_PATH=/path/to/libfastparse.dylib python your_script.py
```

## Examples

From the repository root:

```bash
python3 examples/python/03_binary_decode/binary_decode.py
python3 examples/python/04_inventory_to_sqlite/inventory_to_sqlite.py --workers 12
python3 examples/python/05_diagnostics_scan/diagnostics_scan.py /path/to/java/root --glob "*.java" --workers 12
```

`04_inventory_to_sqlite` is the enterprise pattern for high-throughput work:
the parent Python app reads files, uses threads, decodes binary output into
dataclasses, and writes SQLite tables outside the native library.
