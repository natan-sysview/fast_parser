# Python Binding

The Python binding is a thin `ctypes` wrapper over the FastParse C ABI.

Path:

```text
bindings/python
```

## Local Use From Checkout

```bash
PYTHONPATH=bindings/python python3
```

```python
from fastparse import FastParse

parser = FastParse()
source = b"class Demo { void run() {} }"

result = parser.parse_bytes(
    source,
    language="java",
    output_format="json",
    include_rules=["method_declaration"],
    fields=["rule", "text", "byte_range"],
)

print(parser.version)
print(result.node_count)
print(result.text)
```

## Binary Output

```python
result = parser.parse_bytes(
    source,
    language="java",
    output_format="binary",
    include_rules=["class_declaration", "method_declaration"],
    fields=["id", "parent_id", "rule", "text", "byte_range"],
)

payload = result.data
```

`payload` is MessagePack bytes.

If using the optional `msgpack` package:

```python
import msgpack

document = msgpack.unpackb(payload, raw=False)
```

## Library Loading

The binding searches for the native library under `bin/`.

Override explicitly:

```bash
FASTPARSE_LIBRARY_PATH=/path/to/libfastparse.dylib python3 your_app.py
```

Compatibility:

```bash
TSMP_LIBRARY_PATH=/path/to/libfastparse.dylib python3 your_app.py
```

## API Surface

```text
FastParse(...)
parse_bytes(...)
parse_text(...)
parse_bytes_summary(...)
load_language_extension(...)
language_available(...)
version
ParseResult.data
ParseResult.text
ParseResult.json()
ParseSummary.output_length
ParseSummary.node_count
```

## Language Extensions

Load optional parse languages by path before parsing:

```python
from pathlib import Path
from fastparse import FastParse

parser = FastParse()
load = parser.load_language_extension(Path("bin/libfastparse_language_cobol.dylib"))

assert load.language == "cobol"
assert parser.language_available("cobol")

result = parser.parse_bytes(
    cobol_source_bytes,
    language="cobol",
    output_format="json",
    fields=["rule", "diagnostics"],
)
```

Extension loading is setup work. Do it before starting worker threads.

## Threading

Python applications may call the binding from many threads. The native parser is thread-safe per call.

For high-throughput scans:

- Use threads when the work is mostly native parsing and writing output.
- Use processes only when Python-side CPU work dominates and IPC cost is acceptable.
- Keep SQLite writes in one writer thread/process.
