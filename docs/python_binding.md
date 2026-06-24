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

## Typed Options

Python supports both simple strings/lists and typed options.

```python
from fastparse import FastParse, Field, OutputFormat, ParseOptions

parser = FastParse()
options = ParseOptions(
    language="java",
    output_format=OutputFormat.JSON,
    include_rules=["method_declaration"],
    fields=Field.RULE | Field.TEXT | Field.BYTE_RANGE,
)

result = parser.parse_text("class Demo { void run() {} }", options)
print(result.json())
```

## PyPI / Wheel Use

The public Python package name is:

```text
fastparse
```

Install from PyPI after publication:

```bash
pip install --pre fastparse
```

Install from a GitHub Release wheel:

```bash
pip install fastparse-0.1.0rc17-py3-none-macosx_11_0_arm64.whl
```

Python package versions use PEP 440. A FastParse release named `0.1.0-preview.17` is published to PyPI as `0.1.0rc17`.

The wheel bundles the native library under `fastparse/native/` and includes `py.typed` markers for type-aware tooling. Normal consumers do not need to set `FASTPARSE_LIBRARY_PATH`.

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

Python includes a small schema-specific decoder:

```python
from fastparse import FastParse, Field, OutputFormat, ParseOptions

parser = FastParse()
result = parser.parse_bytes(
    source,
    ParseOptions(
        output_format=OutputFormat.BINARY,
        include_rules=["class_declaration", "method_declaration"],
        fields=Field.ID | Field.PARENT_ID | Field.RULE | Field.TEXT | Field.BYTE_RANGE,
    ),
)

document = result.binary_document()
print(document.schema_version)
print(document.nodes[0].rule)
```

Applications may also decode with the optional `msgpack` package:

```python
import msgpack

document = msgpack.unpackb(payload, raw=False)
```

## Diagnostics Output

Use diagnostics when scanning large corpora for grammar quality:

```python
result = parser.parse_bytes(
    source,
    language="cobol",
    output_format="diagnostics",
)

quality = result.json()
print(quality["hasErrors"], quality["errorNodeCount"])
```

This returns a tiny JSON object and no `nodes` array.

## Enterprise Examples

Python examples live under:

```text
examples/python
```

Recommended examples for real applications:

```bash
python3 examples/python/03_binary_decode/binary_decode.py
```

Decode FastParse binary output into Python dataclasses.

```bash
python3 examples/python/04_inventory_to_sqlite/inventory_to_sqlite.py \
  --inventory-db /path/to/inventario.db \
  --source-root /path/to/componentes \
  --language java \
  --extension java \
  --workers 12 \
  --out-db exports/fastparse_python_ast.sqlite
```

Read an inventory database, parse source files with Python threads, decode binary
MessagePack, and write SQLite tables:

```text
parse_files
ast_nodes
ast_children
```

The default stores the full AST and all fields. Use `--rules` and `--fields`
once the caller knows which grammar rules are needed.

```bash
python3 examples/python/05_diagnostics_scan/diagnostics_scan.py /path/to/source/root \
  --glob "*.java" \
  --language java \
  --workers 12 \
  --out-db exports/fastparse_python_diagnostics.sqlite
```

Scan parse quality using diagnostics-only output. This is the right mode for
grammar evaluation because it avoids materializing the full AST payload.

## Library Loading

The binding first searches the bundled wheel path under `fastparse/native/`, then the local checkout `bin/` path.

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
ParseOptions(...)
parse_bytes(...)
parse_text(...)
parse_bytes_summary(...)
parse_text_summary(...)
load_language_extension(...)
language_available(...)
version
OutputFormat
Field
Normalization
ParseResult.data
ParseResult.text
ParseResult.json()
ParseResult.binary_document()
ParseSummary.output_length
ParseSummary.node_count
BinaryDocument
BinaryNode
BinaryChild
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

## Source Normalization

Python exposes native normalization with the `normalization` option:

```python
result = parser.parse_bytes(
    cobol_source_bytes,
    language="cobol",
    output_format="binary",
    normalization="auto_safe",
)
```

Supported values:

```text
auto_safe
none
cobol_fixed_legacy
```

`auto_safe` is the default. For COBOL it removes known legacy trailer bytes in RAM before parsing, such as final `0x1A`, `0x7F`, NUL, `FHA`, or a lone final `*` record. For modern languages it currently leaves the source untouched.

Use `normalization="none"` when a caller needs byte-for-byte parsing with no cleanup.

## Threading

Python applications may call the binding from many threads. The native parser is thread-safe per call.

For high-throughput scans:

- Use threads when the work is mostly native parsing and writing output.
- Use processes only when Python-side CPU work dominates and IPC cost is acceptable.
- Keep SQLite writes in one writer thread/process.
- Prefer one `FastParse` instance per worker thread for long-running scans.
- Load language extensions before starting worker threads when possible.

## AI-Agent Integration Notes

Agents should treat FastParse as a RAM-only native parser:

- Read files in the parent language.
- Pass `bytes` to `FastParse.parse_bytes`.
- Use `OutputFormat.BINARY` plus `result.binary_document()` for high-throughput structured data.
- Use `OutputFormat.DIAGNOSTICS` for grammar quality scans.
- Store data in SQLite, files, queues, or services outside FastParse.
- Keep package-manager installs normal: `pip install --pre fastparse`.
- Do not write temporary source files just to call FastParse.
