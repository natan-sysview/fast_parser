# FastParse

FastParse is a small native C library for extracting Tree-sitter AST data through stable, FFI-friendly contracts.

The first public version ships with Java support. Parent applications own file I/O, project traversal, persistence, logging, and thread orchestration. FastParse only receives source bytes already in memory and returns AST data in memory.

## What It Does

- Parses source bytes with Tree-sitter.
- Filters AST nodes by grammar rule name.
- Lets callers choose which node fields are returned.
- Returns JSON, CSV, MessagePack binary, or stats.
- Returns diagnostics-only quality reports for large grammar scans.
- Exposes a small C ABI designed for Python, C#, Rust, Java, and other bindings.
- Can load optional language extensions by native library path.
- Can apply safe memory-only normalization for legacy sources such as COBOL trailers.
- Is thread-safe per parse call.

FastParse does not read files, write files, walk directories, create databases, or own thread pools.

## Current Status

```text
Project version      : 0.1.0-preview
C API version        : fastparse-c-api/0.5.0
Binary schema        : 1
Supported languages  : java
Extension preview    : explicit path loading and bundled Python package loading
License              : Apache-2.0
```

The `fastparse_*` symbols are the public names. The older `tsmp_*` symbols remain available as compatibility aliases.

Java is built into the core package. Other parse languages should be delivered as optional language extensions so the default package stays small.

The first packaged extension pilot is Python:

```text
FastParser.Language.Python    NuGet language package
fastparse-language-python     PyPI language wheel
```

Rust is also included as a second local extension-standard pilot:

```text
extensions/rust
grammars/tree-sitter-rust
```

## Quick Start

Build the native library:

```bash
./compila_lib.sh
```

Expected output:

```text
bin/libfastparse.dylib    macOS
bin/libfastparse.so       Linux
bin/fastparse.dll         Windows
```

Run the contract tests:

```bash
python3 -m unittest discover -s tests -v
ctest --test-dir build --output-on-failure
```

Run examples:

```bash
python3 examples/python/01_parse_string/parse_string.py --summary
dotnet run --project examples/csharp/01_parse_string/FastParse.ParseStringExample.csproj
```

## C API

Use:

```c
#include "fastparse.h"
```

Minimal call:

```c
TsmpOptions options = {
    .language = "java",
    .format = TSMP_FORMAT_JSON,
    .include_rules = "method_declaration",
    .fields = TSMP_FIELD_RULE | TSMP_FIELD_TEXT | TSMP_FIELD_BYTE_RANGE,
    .include_tokens = 0,
    .pretty = 0
};

TsmpResult result = {0};
int status = fastparse_parse(source_bytes, source_len, &options, &result);

if (status == TSMP_OK && result.status == TSMP_OK) {
    /* result.data contains result.length bytes */
}

fastparse_result_free(&result);
```

Every successful or failed parse call that receives a `TsmpResult` must be followed by exactly one `fastparse_result_free(&result)`.

## Language Extensions

FastParse can load a native language extension before parsing.

Advanced users can load an explicit native extension path:

```c
FastParseLanguageLoadResult load = {0};
int status = fastparse_load_language_extension("/path/to/libfastparse_language_cobol.dylib", &load);
fastparse_language_load_result_free(&load);
```

After loading, use the registered language name in normal parse options:

```c
.language = "cobol"
```

Extension loading is a setup step. Load extensions before starting concurrent parse workers.

Package-manager language extensions are loaded by bindings with the bundled-language API:

```python
from fastparse import FastParse

parser = FastParse()
parser.load_bundled_language("python")
result = parser.parse_text("def hello(): pass", language="python")
```

```csharp
using var parser = new FastParseClient();
parser.LoadBundledLanguage("python");
```

Official grammar extensions must follow [FastParse Grammar Standard](docs/grammar_standard.md).

## Source Normalization

New bindings use `auto_safe` normalization by default. Modern languages are left unchanged. For COBOL, FastParse removes known legacy trailer bytes in RAM before parsing, such as final `0x1A`, `0x7F`, NUL, `FHA`, or a lone final `*` record.

Use `none` when the caller needs byte-for-byte parsing with no cleanup. Normalization does not write to disk and does not change the output field contract.

## Output Formats

| Format | Native constant | Use case |
|---|---|---|
| JSON | `TSMP_FORMAT_JSON` | Human-readable integration and development. |
| CSV | `TSMP_FORMAT_CSV` | Tabular export, spreadsheets, quick inspection. |
| Binary | `TSMP_FORMAT_BINARY` | High-performance program-to-program exchange. |
| Stats | `TSMP_FORMAT_STATS` | Count matching nodes without serializing AST output. |
| Diagnostics | `TSMP_FORMAT_DIAGNOSTICS` | Parse-quality counters without serializing AST nodes. |

Binary output is MessagePack schema version 1. Node `text` is encoded as MessagePack `bin`, not as a string, so source bytes are preserved without Unicode assumptions.

## Production Pattern

During exploration:

```text
rules  = all
fields = all
format = json or binary
```

After the application knows what it needs:

```text
rules  = class_declaration|method_declaration|field_declaration
fields = id,parent_id,rule,text,byte_range
format = binary
```

This avoids creating huge AST payloads when the caller only needs specific grammar rules.

## Bindings

Current bindings:

```text
bindings/python
bindings/csharp/FastParse
```

Bindings are reusable code intended for application developers. Runnable demos and lab applications live under `examples/`.

## Documentation

- [Contracts](docs/contracts.md)
- [C API](docs/c_api.md)
- [Output Formats](docs/output_formats.md)
- [Binary MessagePack Schema](docs/binary_schema.md)
- [Binding Contracts](docs/bindings.md)
- [Python Binding](docs/python_binding.md)
- [C# Binding](docs/csharp_binding.md)
- [AI Agent Integration Guide](docs/ai_agent_integration.md)
- [Encoding And Bytes Contract](docs/encoding.md)
- [Threading, Platforms, And Packaging](docs/packaging.md)
- [Language Strategy](docs/languages.md)
- [Language Extensions](docs/language_extensions.md)
- [FastParse Grammar Standard](docs/grammar_standard.md)
- [Java Inventory SQLite Lab](docs/java_inventory.md)
- [Benchmarks](docs/benchmarks.md)
- [Release Checklist](docs/release_checklist.md)
- [GitHub Publish Guide](docs/github_publish.md)
- [Package Registry Setup](docs/package_registry_setup.md)

## Repository Layout

```text
include/        Public C headers.
src/            Native C implementation.
grammars/       Vendored Tree-sitter grammars.
extensions/     Experimental optional language extensions.
vendor/         Vendored Tree-sitter runtime pieces.
bindings/       Reusable language bindings.
examples/       Runnable examples and lab apps.
tests/          Native and binding contract tests.
tools/          Internal maintenance and benchmark scripts.
docs/           Public contracts and design notes.
```

## License

FastParse is licensed under Apache-2.0. See [LICENSE](LICENSE).

Vendored third-party notices are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
