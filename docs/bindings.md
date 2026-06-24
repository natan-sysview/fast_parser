# Binding Contracts

FastParse exposes a small C ABI so parent languages can build thin, predictable bindings.

Target bindings:

```text
Python
C#
Rust
Java
```

The native layer owns parsing and AST serialization. The binding layer owns library loading, option ergonomics, memory cleanup, and language-native result types.

## Required Native Calls

Every binding should wrap exactly these native functions first:

```c
const char *fastparse_version(void);

int fastparse_parse(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptions *options,
    TsmpResult *out_result);

void fastparse_result_free(TsmpResult *result);
```

The older `tsmp_*` symbols remain available as compatibility aliases.

## Binding-Level API Shape

Recommended high-level API:

```text
parse_bytes(source_bytes, options) -> ParseResult
parse_text(source_text, encoding="utf-8", options) -> ParseResult
version() -> string
```

`parse_bytes` is the primary contract.

`parse_text` is a convenience wrapper that encodes text before calling the native library.

## Result Shape

Recommended binding result:

```text
status
format
data_bytes
data_text
node_count
error_message
```

Bindings may expose `data_text` only for JSON/CSV convenience, but they should keep `data_bytes` available because FastParse returns byte buffers.

For `TSMP_FORMAT_BINARY`, `data_bytes` contains MessagePack and should be decoded with a MessagePack library in the parent language.

For `TSMP_FORMAT_STATS`:

```text
data_bytes = empty
node_count = populated
```

## Memory Ownership

Native memory returned through `TsmpResult` must always be released by:

```c
fastparse_result_free(&result);
```

Binding cleanup patterns:

| Binding | Recommended cleanup |
|---|---|
| Python | `try/finally` around `ctypes` call. |
| C# | `try/finally` or `SafeHandle`/`IDisposable`. |
| Rust | `Drop` implementation around an owned result wrapper. |

Bindings should copy native `result.data` into a managed/runtime-owned buffer before freeing the native result.

## Threading

`fastparse_parse` is thread-safe per call.

Bindings may allow concurrent calls as long as:

- The source buffer remains immutable until the call returns.
- Each call uses its own `TsmpResult`.
- Each result is freed exactly once.

The native library does not create or manage thread pools. Parent runtimes decide how many threads to use.

## Encoding

Bindings should not silently transcode raw bytes.

Recommended policy:

```text
parse_bytes: pass bytes unchanged
parse_text: encode using an explicit/default encoding
```

JSON output is valid UTF-8 JSON. For exact source recovery, expose byte ranges to users and document that `text` is a serialized representation, not a byte-for-byte transport.

## Options Mapping

Bindings should expose friendly names while preserving native behavior.

Recommended field names:

```text
id
parent_id
rule
text
range
byte_range
child_count
children
all
```

Recommended formats:

```text
json
csv
binary
msgpack
stats
```

Recommended options object:

```text
language: string = "java"
format: "json" | "csv" | "binary" | "msgpack" | "stats" = "json"
include_rules: list<string> | string | null = null
fields: list<string> | bitmask | null = null
include_tokens: bool = false
pretty: bool = false
normalization: "auto_safe" | "none" | "cobol_fixed_legacy" = "auto_safe"
```

`fields = null` should map to native `fields = 0`, which means all fields.

`include_rules = null` or empty should map to all named nodes.

`normalization = "auto_safe"` should map to `TSMP_NORMALIZATION_AUTO_SAFE` when the native library supports `fastparse_parse_v2`. Bindings may fall back to `fastparse_parse` for older native libraries only when the caller did not request explicit normalization.

## Error Mapping

Bindings should convert non-zero native status into language-native errors.

Recommended exception/error names:

| Native status | Binding error |
|---|---|
| `TSMP_ERROR_INVALID_ARGUMENT` | Invalid argument / value error. |
| `TSMP_ERROR_UNSUPPORTED_LANGUAGE` | Unsupported language. |
| `TSMP_ERROR_PARSE_FAILED` | Parse failed. |
| `TSMP_ERROR_UNSUPPORTED_FORMAT` | Unsupported format. |
| `TSMP_ERROR_OUT_OF_MEMORY` | Native allocation failure. |

The binding should include `result.error_message` in the raised error when available.

## Binary MessagePack Contract

`TSMP_FORMAT_BINARY` is MessagePack.

Top-level object:

```text
format: "tsmp-binary"
schemaVersion: 1
language: string
nodes: array
nodeCount: integer
```

Node objects use the same selected fields as JSON/CSV:

```text
id
parentId
rule
text
startLine
startColumn
endLine
endColumn
startByte
endByte
childCount
children
```

Binary-specific rule:

```text
text -> MessagePack bin bytes
```

That is intentional. It avoids Unicode assumptions and preserves source bytes exactly for Rust, C#, Python, Java, and other consumers.

Recommended decoders:

| Language | Decoder family |
|---|---|
| Python | `msgpack` |
| C# | MessagePack-CSharp |
| Rust | `rmp` / `rmp-serde` |
| Java | msgpack-java |

## Python Binding

The project includes a Python binding:

```text
bindings/python/fastparse
```

Use it from the checkout:

```bash
PYTHONPATH=bindings/python python3
```

Example:

```python
from fastparse import FastParse

parser = FastParse()
result = parser.parse_bytes(
    b"class Demo { void run() {} }",
    language="java",
    output_format="json",
    include_rules=["method_declaration"],
    fields=["rule", "text", "byte_range"],
)

print(parser.version)
print(result.node_count)
print(result.json())
```

The binding supports:

- `parse_bytes(...)`
- `parse_text(...)`
- `ParseResult.data`
- `ParseResult.text`
- `ParseResult.json()`
- `FASTPARSE_LIBRARY_PATH` for explicit native library loading.
- `TSMP_LIBRARY_PATH` as a compatibility fallback.

The example CLIs use this package:

```text
examples/python/01_parse_string/parse_string.py
examples/python/02_bulk_probe/bulk_probe.py
```

## C# Notes

Use P/Invoke against:

```text
fastparse.dll
libfastparse.dylib
libfastparse.so
```

The lab includes a first C# binding:

```text
bindings/csharp/FastParse
```

Example project:

```text
examples/csharp/01_parse_string
```

Run:

```bash
dotnet run --project examples/csharp/01_parse_string/FastParse.ParseStringExample.csproj
```

The C# wrapper:

- Loads `libfastparse.dylib`, `libfastparse.so`, or `fastparse.dll`.
- Prefers `fastparse_*` native symbols.
- Falls back to `tsmp_*` compatibility symbols.
- Exposes `FastParseClient.ParseBytes(...)`.
- Exposes `FastParseClient.ParseText(...)`.
- Exposes `FastParseClient.ParseBytesSummary(...)`.
- Copies native output into managed `byte[]`.
- Frees native memory with `fastparse_result_free`.

Current binary support returns MessagePack bytes in `ParseResult.Data`. Decoding with MessagePack-CSharp can be added in a higher-level package or application layer.

The binding also includes a minimal schema-specific decoder:

```csharp
var document = FastParseMessagePack.Decode(result.Data);

Console.WriteLine(document.SchemaVersion);
Console.WriteLine(document.Nodes[0].Rule);
Console.WriteLine(document.Nodes[0].Text); // byte[]
```

This decoder understands the FastParse schema v1 and avoids external dependencies.

## Rust Notes

Use a low-level `extern "C"` module plus a safe wrapper.

The safe wrapper should:

- Own copied result bytes.
- Free native results through `Drop`.
- Represent field masks with bitflags.
- Represent formats and errors with Rust enums.

## Java Notes

Use JNA or JNI against:

```text
fastparse.dll
libfastparse.dylib
libfastparse.so
```

JNA is easier for a first binding. JNI is more work but can be tuned harder later.

The Java wrapper should expose byte-first APIs:

```text
parseBytes(byte[] source, Options options)
parseText(String source, Charset charset, Options options)
```

For `binary`, Java should decode MessagePack with msgpack-java and keep `text` fields as `byte[]`.
