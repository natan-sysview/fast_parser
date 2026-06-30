# Java Frameworks FastParse Usage

## Purpose

Use `java-frameworks` when Java source code must be parsed with framework-oriented grammar nodes and framework evidence queries. Keep FastParse's built-in `java` language for normal Java parsing.

## Build

From the lab root:

```sh
cmake -S . -B build-java-frameworks-formal
cmake --build build-java-frameworks-formal --target tsmp fastparse_language_java_frameworks
```

The promoted grammar is expected at:

```text
grammars/tree-sitter-java-frameworks
```

The local extension library is emitted to:

```text
bin/libfastparse_language_java_frameworks.dylib
```

On Linux the extension suffix is `.so`; on Windows it is `.dll`.

## C#

```csharp
using FastParse;

var parser = new FastParseClient("/path/to/libfastparse.dylib");
parser.LoadLanguageExtension("/path/to/libfastparse_language_java_frameworks.dylib");

var parse = parser.ParseText(
    source,
    language: "java-frameworks",
    outputFormat: "binary",
    fields: new[] { "rule", "diagnostics" });

var query = File.ReadAllText("/path/to/extensions/java-frameworks/queries/frameworks.scm");
var captures = parser.QueryText(
    source,
    query,
    language: "java-frameworks",
    outputFormat: "json",
    fields: new[] { "capture_name", "rule", "text", "range" });
```

## Python

```python
from pathlib import Path
from fastparse import FastParse

lab = Path("/path/to/tree-sitter-multi-parser-lab")
parser = FastParse(lab / "bin/libfastparse.dylib")
parser.load_language_extension(lab / "bin/libfastparse_language_java_frameworks.dylib")

source = Path("Example.java").read_bytes()
result = parser.parse_bytes(
    source,
    language="java-frameworks",
    output_format="binary",
    fields=["rule", "diagnostics"],
    include_tokens=False,
)

query = (lab / "extensions/java-frameworks/queries/frameworks.scm").read_bytes()
captures = parser.query_bytes(
    source,
    query,
    language="java-frameworks",
    output_format="json",
    fields=["capture_name", "rule", "text", "range"],
)
```

## Local Inventory Validation

Run the full framework inventory validation from the lab root:

```sh
experimental-grammars/tree-sitter-java-frameworks/tools/validate_fastparse_extension.py --workers 12
```

The validator reads source bytes, normalizes only parser input, loads the native extension before parsing in worker threads, uses MessagePack diagnostics, and stores compact evidence in:

```text
experimental-grammars/tree-sitter-java-frameworks/runs/java_frameworks_fastparse_validation.sqlite
experimental-grammars/tree-sitter-java-frameworks/audits/java_frameworks_fastparse_extension_validation.md
```

## Query Asset

The extension ships the framework evidence query at:

```text
extensions/java-frameworks/queries/frameworks.scm
```

FastParse loads the native language extension. Query execution remains an explicit caller action.
