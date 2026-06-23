# FastParse Language Extensions

FastParse supports a small core library plus optional language extensions.

This document defines the professional package-manager-first model for adding parseable languages such as COBOL, PL/SQL, Python, Rust, or other Tree-sitter grammars without making the core package heavy.

Terminology:

- Host language: the language used by the application, for example C#, Python, Rust, Java, or C.
- Parse language: the language being parsed, for example Java, COBOL, PL/SQL, Python, or Rust.
- Core package: FastParse runtime, C ABI, bindings, output formats, memory handling, and Java default grammar.
- Language extension: optional package that adds one parse language.

## Goals

Status: `Stable`

The extension system must support:

- Small default install size.
- Java included in the default core package.
- Optional parse languages installed only when needed.
- Package-manager installation for humans and AI agents.
- No manual copying of native libraries.
- No source recompilation for ordinary users.
- Consistent naming across NuGet, PyPI, crates.io, and future Maven packages.
- Explicit loading by path for advanced users.
- Automatic/bundled loading from installed packages for normal users.
- The existing memory-only parse contract: source bytes in RAM, output in RAM.

Non-goals:

- FastParse core does not scan arbitrary directories for plugins.
- FastParse core does not download extensions at runtime.
- FastParse core does not manage package managers.
- FastParse parse calls do not read source files from disk.

## Distribution Model

Status: `Stable` for naming pattern; `Preview` for exact package internals.

Default install:

```text
FastParser core + Java support
```

Optional language install:

```text
FastParser core + FastParser language extension package
```

Recommended package names:

| Ecosystem | Core package | COBOL extension | PL/SQL extension |
|---|---|---|---|
| NuGet | `FastParser` | `FastParser.Language.Cobol` | `FastParser.Language.Plsql` |
| PyPI | `fastparser` | `fastparser-language-cobol` | `fastparser-language-plsql` |
| crates.io | `fastparser` | `fastparser-language-cobol` | `fastparser-language-plsql` |
| Maven | `io.fastparser:fastparser` | `io.fastparser:fastparser-language-cobol` | `io.fastparser:fastparser-language-plsql` |

Package names must be predictable so an AI coding agent can infer the install command from a requested language.

## Agent-Friendly Install Commands

Status: `Stable` as documentation convention.

When a user asks for COBOL parsing, an AI agent should install both the core binding and the language extension for the host ecosystem.

C# / NuGet:

```bash
dotnet add package FastParser
dotnet add package FastParser.Language.Cobol
```

Python / PyPI:

```bash
pip install fastparser
pip install fastparser-language-cobol
```

Rust / crates.io:

```bash
cargo add fastparser
cargo add fastparser-language-cobol
```

Java / Maven:

```xml
<dependency>
  <groupId>io.fastparser</groupId>
  <artifactId>fastparser</artifactId>
  <version>...</version>
</dependency>
<dependency>
  <groupId>io.fastparser</groupId>
  <artifactId>fastparser-language-cobol</artifactId>
  <version>...</version>
</dependency>
```

The same pattern applies to other languages:

```text
FastParser.Language.Plsql
fastparser-language-plsql
```

## User-Facing API

Status: `Preview`

Bindings should support two loading modes.

### Explicit Path Loading

For advanced tooling, local builds, enterprise deployments, or tests:

```text
load_language_extension(path)
```

This mode is implemented in the native C API, Python binding, and C# binding.

Example C# shape:

```csharp
using var parser = new FastParseClient();
parser.LoadLanguageExtension("/path/to/fastparse-language-cobol");
```

### Bundled Package Loading

For normal package-manager installs:

```text
load_bundled_language(language)
```

Example C# shape:

```csharp
using var parser = new FastParseClient();
parser.LoadBundledLanguage("cobol");

var result = parser.ParseText(cobolSource, new ParseOptions
{
    Language = "cobol",
    Format = FastParseFormat.Json
});
```

Example Python shape:

```python
from fastparser import FastParser

parser = FastParser()
parser.load_bundled_language("cobol")
result = parser.parse_text(cobol_source, language="cobol", output_format="json")
```

Example Rust shape:

```rust
let mut parser = fastparser::Parser::new()?;
fastparser_language_cobol::register(&mut parser)?;

let result = parser.parse_text(cobol_source, ParseOptions {
    language: "cobol",
    format: OutputFormat::Json,
    ..Default::default()
})?;
```

## Native Extension Layout

Status: `Preview`

A language extension package should contain one native dynamic library per supported platform and a machine-readable manifest.

Conceptual layout:

```text
fastparse-language-cobol/
  manifest.json
  docs/
  queries/
  runtimes/linux-x64/native/libfastparse_language_cobol.so
  runtimes/osx-arm64/native/libfastparse_language_cobol.dylib
  runtimes/osx-x64/native/libfastparse_language_cobol.dylib
  runtimes/win-x64/native/fastparse_language_cobol.dll
```

For unpacked native release archives:

```text
manifest.json
lib/libfastparse_language_cobol.so
lib/libfastparse_language_cobol.dylib
bin/fastparse_language_cobol.dll
docs/
queries/
```

## Extension Manifest

Status: `Preview`

Every extension should include a manifest.

Example:

```json
{
  "extensionKind": "fastparse-language",
  "language": "cobol",
  "displayName": "COBOL",
  "version": "0.1.0",
  "abi": "fastparse-language-extension/1",
  "coreAbi": "fastparse-c-api/0.4.0",
  "grammar": {
    "name": "tree-sitter-cobol",
    "source": "https://github.com/example/tree-sitter-cobol",
    "revision": "..."
  },
  "symbols": {
    "descriptor": "fastparse_language_extension_descriptor",
    "treeSitterLanguage": "tree_sitter_cobol"
  },
  "aliases": ["cbl", "cob"],
  "queries": [],
  "platforms": [
    "linux-x64",
    "osx-arm64",
    "osx-x64",
    "win-x64"
  ]
}
```

Rules:

- `extensionKind` must be `fastparse-language`.
- `language` is the canonical parse language name.
- `language` must be lowercase and package-friendly.
- `abi` identifies the language extension ABI.
- `coreAbi` identifies the compatible FastParse core ABI.
- `symbols.treeSitterLanguage` names the exported Tree-sitter language function.
- `aliases` are optional convenience names and must never replace the canonical name.
- `queries` are optional and may be used later for named extraction presets.

## Native Extension ABI

Status: `Preview`

The language extension dynamic library should export stable symbols.

Recommended first ABI:

```c
const char *fastparse_language_extension_version(void);
const FastParseLanguageDescriptor *fastparse_language_extension_descriptor(void);
const TSLanguage *tree_sitter_cobol(void);
```

Conceptual descriptor:

```c
typedef struct {
    uint32_t abi_version;
    const char *language;
    const char *display_name;
    const char *tree_sitter_symbol;
    const char **aliases;
    size_t alias_count;
} FastParseLanguageDescriptor;
```

Rules:

- The descriptor memory is owned by the extension and remains valid while the extension is loaded.
- The core validates ABI compatibility before registering the language.
- The core registers `language` as the canonical name.
- The core may register aliases as convenience names.
- If the ABI is incompatible, loading fails with a controlled error.

## Core C ABI Additions

Status: `Preview`

The core currently exposes explicit path loading and language availability:

```c
int fastparse_load_language_extension(
    const char *path,
    FastParseLanguageLoadResult *out_result);

int fastparse_language_available(
    const char *language);

void fastparse_language_load_result_free(
    FastParseLanguageLoadResult *result);
```

Future registry APIs may add:

```c
int fastparse_list_languages(...);
int fastparse_register_language(...);
```

Possible binding-level names:

```text
load_language_extension(path)
load_bundled_language(language)
language_available(language)
list_languages()
```

Current implementation status:

```text
load_language_extension(path)  implemented
language_available(language)   implemented
load_bundled_language(language) planned
list_languages()               planned
```

Extension loading is a setup step. Applications should load extensions before starting concurrent parse workers.

## Experimental COBOL Extension

Status: `Preview`

The repository contains a first experimental COBOL extension host:

```text
extensions/cobol/fastparse_language_cobol.c
```

To build it locally, point CMake at a `tree-sitter-cobol` checkout:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
  -DFASTPARSE_COBOL_GRAMMAR_DIR=/path/to/tree-sitter-cobol
cmake --build build --config Release
```

Expected output on macOS:

```text
bin/libfastparse_language_cobol.dylib
```

Use it from Python:

```python
parser = FastParser()
parser.load_language_extension("bin/libfastparse_language_cobol.dylib")
result = parser.parse_bytes(source, language="cobol", fields=["rule", "diagnostics"])
```

This is not packaged as `FastParser.Language.Cobol` yet. The first goal is to evaluate grammar quality against real COBOL corpora using diagnostics.

## NuGet Discovery

Status: `Preview`

NuGet extension packages should use RID-specific native assets:

```text
runtimes/linux-x64/native/libfastparse_language_cobol.so
runtimes/osx-arm64/native/libfastparse_language_cobol.dylib
runtimes/osx-x64/native/libfastparse_language_cobol.dylib
runtimes/win-x64/native/fastparse_language_cobol.dll
```

The package may also include:

```text
buildTransitive/FastParser.Language.Cobol.targets
contentFiles/any/any/fastparse/languages/cobol/manifest.json
docs/
```

Expected developer flow:

```bash
dotnet add package FastParser
dotnet add package FastParser.Language.Cobol
```

Expected C# flow:

```csharp
using var parser = new FastParseClient();
parser.LoadBundledLanguage("cobol");
```

Discovery options:

- The extension package copies manifest/native assets to the build output through `.targets`.
- The FastParser C# binding searches known output locations.
- Advanced users pass an explicit extension path.

## PyPI Discovery

Status: `Preview`

Python extension wheels should place native assets inside the installed package.

Conceptual package:

```text
fastparser_language_cobol/
  __init__.py
  manifest.json
  native/
    linux-x64/libfastparse_language_cobol.so
    osx-arm64/libfastparse_language_cobol.dylib
    osx-x64/libfastparse_language_cobol.dylib
    win-x64/fastparse_language_cobol.dll
```

Expected developer flow:

```bash
pip install fastparser
pip install fastparser-language-cobol
```

Expected Python flow:

```python
parser = FastParser()
parser.load_bundled_language("cobol")
```

Discovery should use Python package metadata and `importlib.resources`, not hard-coded global paths.

## crates.io Discovery

Status: `Preview`

Rust extension crates should expose registration helpers.

Expected developer flow:

```bash
cargo add fastparser
cargo add fastparser-language-cobol
```

Expected Rust flow:

```rust
let mut parser = fastparser::Parser::new()?;
fastparser_language_cobol::register(&mut parser)?;
```

The extension crate may:

- Bundle native assets.
- Build/link the grammar as part of the crate.
- Expose a path to a bundled dynamic extension.
- Expose a Rust function that calls the FastParse registration API.

The selected Rust strategy must keep the public FastParse parse contract unchanged.

## Static Custom Builds

Status: `Preview`

Some organizations may want one native library with a fixed language set.

Supported model:

```text
fastparse-core + selected grammars -> one custom libfastparse
```

Rules:

- Static custom builds must expose the same C ABI.
- `fastparse_list_languages` should report built-in languages.
- Unsupported languages return the same controlled unsupported-language error.
- Static builds are packaging variants, not different APIs.

## Package Size Strategy

Status: `Stable`

The core package must remain small.

Rules:

- Java stays built into the default preview core.
- Large or specialized grammars should live in language extension packages.
- Developers install only the parse languages they need.
- Adding a language extension must not require reinstalling every other language.

This avoids returning to a monolithic package with many unused grammars.

## Grammar Quality Diagnostics

Status: `Stable` for diagnostic field names; `Preview` for extension quality scoring.

Language extensions should be evaluated with FastParse diagnostics enabled.

Recommended fields for grammar evaluation:

```text
TSMP_FIELD_RULE
TSMP_FIELD_BYTE_RANGE
TSMP_FIELD_RANGE
TSMP_FIELD_DIAGNOSTICS
```

These fields expose:

```text
hasErrors
errorNodeCount
missingNodeCount
errorByteCount
isError
isMissing
hasError
```

Rules:

- A language extension can parse successfully and still report grammar errors.
- `hasErrors = true` means Tree-sitter recovered from unsupported, invalid, or incomplete syntax.
- Grammar quality tests should store diagnostics per source file.
- Extension maintainers should track diagnostic rates over real corpora before promoting a grammar.
- Multiple grammar implementations for the same parse language may be compared by their diagnostic rates.

Recommended corpus metrics:

```text
files_parsed
files_with_errors
error_node_count
missing_node_count
error_byte_count
error_bytes_per_kloc
most_common_error_parent_rules
```

For COBOL, this lets FastParse compare candidate grammars against large enterprise corpora and choose the most robust implementation before publishing a stable extension.

## Versioning Strategy

Status: `Preview`

The core and extensions have separate versions.

Example:

```text
FastParser                  0.1.0
FastParser.Language.Cobol   0.1.0
FastParser.Language.Plsql   0.1.0
```

Compatibility should be determined by:

```text
core ABI version
language extension ABI version
grammar revision
binary schema version
package version
```

Rules:

- Patch releases may fix packaging or grammar bugs.
- Minor releases may add optional fields or language capabilities.
- Breaking extension ABI changes require a new extension ABI version.
- Breaking binary output changes require a new binary schema version.

## Security And Trust

Status: `Preview`

Language extensions are native code. Installing one is equivalent to installing any other native package.

Recommended safeguards:

- Publish extensions from the official FastParse organization/account.
- Include checksums in GitHub Releases.
- Use package-manager trust mechanisms where available.
- Publish provenance/SBOM when available.
- Document grammar source and revision.
- Avoid loading arbitrary untrusted extension paths.

Bindings should make automatic discovery package-scoped, not filesystem-wide.

## Troubleshooting Contract

Status: `Preview`

Bindings should report clear errors for:

- Extension package not installed.
- Native extension asset missing for current platform.
- Extension ABI incompatible with core.
- Language name not found after loading.
- Native dynamic library load failure.
- Missing Tree-sitter language symbol.

Error messages should include:

```text
requested language
current platform/RID
candidate package name
candidate path when applicable
core ABI version
extension ABI version when available
```

## Roadmap

Status: `Preview`

Recommended implementation order:

1. Keep Java built into core.
2. Finalize this extension contract.
3. Add core registry APIs: list/load/available.
4. Build a first experimental extension from an existing grammar.
5. Publish a NuGet extension package first.
6. Replicate the pattern for PyPI.
7. Replicate the pattern for crates.io.
8. Add Maven/JVM packaging later.

Good first extension candidates:

```text
plsql
cobol
python
rust
csharp
```

Choose the first candidate based on grammar quality, scanner complexity, and available real-world test corpus.
