# TSMP Python Binding

Small `ctypes` binding for the TSMP native C library.

The binding keeps the same design boundary as the native library:

- Python owns file I/O.
- Python passes bytes already loaded in RAM.
- TSMP returns JSON, CSV, MessagePack binary, or stats in RAM.
- Python copies the returned native buffer and frees the native result.

## Quick Use

```python
from tsmp import Tsmp

tsmp = Tsmp()
source = b"class Demo { void run() {} }"

result = tsmp.parse_bytes(
    source,
    language="java",
    output_format="json",
    fields=["rule", "text", "byte_range"],
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

If the caller only needs node/output counts and does not need to copy the generated JSON/CSV into Python:

```python
summary = tsmp.parse_bytes_summary(
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
