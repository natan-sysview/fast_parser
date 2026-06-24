# FastParse Python Binding

Small `ctypes` binding for the FastParse native C library.

The binding keeps the same design boundary as the native library:

- Python owns file I/O.
- Python passes bytes already loaded in RAM.
- FastParse returns JSON, CSV, MessagePack binary, diagnostics, or stats in RAM.
- Python copies the returned native buffer and frees the native result.

## Install

From PyPI, once the package is published:

```bash
pip install fastparse
```

From a downloaded wheel:

```bash
pip install fastparse-0.1.0rc16-py3-none-macosx_11_0_arm64.whl
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

Binary MessagePack output:

```python
result = tsmp.parse_bytes(
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
