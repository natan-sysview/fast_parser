# FastParse Grammar Standard

This document defines the standard every FastParse parse-language grammar must follow before it becomes an official language extension.

It is written for maintainers, binding authors, and AI coding agents that will add languages such as COBOL, PL/SQL, Python, Rust, C#, or future legacy grammars.

Status labels:

- `Stable`: intended to remain compatible within the `0.1.x` release line.
- `Preview`: usable now, but may change before the first stable extension release.
- `Internal`: implementation detail; consumers must not depend on it.

## Core Principle

Status: `Stable`

A FastParse grammar is not an application. It is a parse-language capability loaded by the FastParse core.

Rules:

- The parent application owns file I/O, databases, queues, retries, and persistence.
- FastParse receives source bytes already in RAM.
- The grammar returns Tree-sitter syntax through the FastParse output contracts.
- The grammar must not create output files, databases, indexes, or reports.
- The grammar must not require temporary source files for normal parse calls.

## Grammar Lifecycle

Status: `Stable`

Every official grammar moves through these stages:

```text
candidate -> experimental -> preview -> stable
```

Candidate:

- Grammar source identified.
- License checked.
- Build can produce a local dynamic extension.
- At least one smoke sample parses.

Experimental:

- FastParse extension descriptor exports successfully.
- Diagnostics scan can run over a real corpus.
- Known normalization needs are documented.
- Known parser hangs or pathological files are tracked.

Preview:

- Package-manager install path exists for at least one host ecosystem.
- GitHub Release assets exist for supported platforms.
- Local and CI smoke tests parse sample source as JSON, Binary, and Diagnostics.
- AI-agent install and usage docs exist.
- Compatibility with a FastParse core ABI is declared.

Stable:

- Rule and field behavior is documented.
- Diagnostics quality baseline is measured over a representative corpus.
- Extension package has public-registry post-publish smoke tests.
- Breaking changes follow the versioning policy in this document.

## Canonical Language Name

Status: `Stable`

Each grammar must define one canonical parse language name.

Rules:

- Lowercase only.
- ASCII letters, digits, and hyphen are allowed.
- Prefer simple names without punctuation.
- The canonical name is what callers pass in `ParseOptions.language`.
- Aliases may be added later, but must never replace the canonical name.

Recommended canonical names:

```text
java
cobol
plsql
python
rust
csharp
javascript
typescript
```

Avoid:

```text
CSharp
c#
tree-sitter-c-sharp
PL/SQL
```

## Package Naming

Status: `Stable`

Package names must be predictable so humans and AI agents can infer them.

| Ecosystem | Core package | Language package pattern | COBOL example |
|---|---|---|---|
| NuGet | `FastParser` | `FastParser.Language.<Name>` | `FastParser.Language.Cobol` |
| PyPI | `fastparse` | `fastparse-language-<name>` | `fastparse-language-cobol` |
| crates.io | `fastparse` | `fastparse-language-<name>` | `fastparse-language-cobol` |
| Maven | `io.fastparser:fastparser` | `io.fastparser:fastparser-language-<name>` | `io.fastparser:fastparser-language-cobol` |

Package names must match the canonical language name except where ecosystem naming conventions require casing.

## Source Layout

Status: `Preview`

Recommended source layout for an official grammar extension:

```text
extensions/<language>/
  README.md
  manifest.json
  samples/
    smoke.<ext>
    errors.<ext>
  queries/
  tests/
  fastparse_language_<language>.c
```

Tree-sitter grammar source may be:

- Vendored under `grammars/tree-sitter-<name>/` when license and size allow.
- Fetched by CI from a pinned revision.
- Provided by an external path for local experimental builds.

Required Tree-sitter files:

```text
src/parser.c
```

Optional scanner files:

```text
src/scanner.c
src/scanner.cc
```

C++ scanners are allowed, but the extension build must explicitly support C++ linking on Linux, macOS, and Windows.

## Native Extension ABI

Status: `Preview`

Current extension ABI version:

```text
1
```

Every dynamic language extension must export:

```c
const FastParseLanguageDescriptor *fastparse_language_extension_descriptor(void);
```

Current descriptor shape:

```c
typedef struct {
    unsigned int abi_version;
    const char *language;
    const char *display_name;
    const char *tree_sitter_symbol;
    FastParseLanguageFn language_fn;
} FastParseLanguageDescriptor;
```

Rules:

- `abi_version` must match the FastParse extension ABI supported by the core.
- `language` is the canonical parse language name.
- `display_name` is a human-readable name.
- `tree_sitter_symbol` is the Tree-sitter function name for diagnostics and manifest validation.
- `language_fn` returns the Tree-sitter `TSLanguage`.
- Descriptor memory is owned by the extension and remains valid while the dynamic library is loaded.
- Loading must fail with a controlled error when the ABI is incompatible.

Minimal extension example:

```c
#include "tsmp.h"

#ifdef _WIN32
#define FASTPARSE_EXTENSION_API __declspec(dllexport)
#else
#define FASTPARSE_EXTENSION_API __attribute__((visibility("default")))
#endif

extern const TSLanguage *tree_sitter_COBOL(void);

static const FastParseLanguageDescriptor LANGUAGE = {
    1u,
    "cobol",
    "COBOL",
    "tree_sitter_COBOL",
    tree_sitter_COBOL
};

FASTPARSE_EXTENSION_API const FastParseLanguageDescriptor *fastparse_language_extension_descriptor(void)
{
    return &LANGUAGE;
}
```

Future ABI versions may add aliases, semantic version metadata, query metadata, or feature flags. They must not change ABI version `1` layout.

## Extension Manifest

Status: `Preview`

Every packaged grammar should include a machine-readable manifest.

Recommended manifest:

```json
{
  "extensionKind": "fastparse-language",
  "language": "cobol",
  "displayName": "COBOL",
  "version": "0.1.0-preview.1",
  "extensionAbi": 1,
  "coreAbi": "fastparse-c-api/0.5.0",
  "binarySchemaVersion": 1,
  "grammar": {
    "name": "tree-sitter-cobol",
    "source": "https://example.com/tree-sitter-cobol",
    "revision": "pinned-commit-or-tag",
    "license": "..."
  },
  "symbols": {
    "descriptor": "fastparse_language_extension_descriptor",
    "treeSitterLanguage": "tree_sitter_COBOL"
  },
  "normalization": {
    "default": "auto_safe",
    "supported": ["auto_safe", "none", "cobol_fixed_legacy"]
  },
  "platforms": [
    "linux-x64",
    "osx-arm64",
    "osx-x64",
    "win-x64"
  ],
  "status": "preview"
}
```

Rules:

- `extensionKind` must be `fastparse-language`.
- `language` must equal the canonical language name.
- `extensionAbi` must match the descriptor ABI.
- `coreAbi` declares the minimum compatible FastParse core C ABI.
- `grammar.revision` must be pinned for reproducible builds.
- `symbols.treeSitterLanguage` must match the descriptor.
- `platforms` lists the platforms included by the package, not hoped-for platforms.

## Output Compatibility

Status: `Stable`

All grammars must use the same FastParse output contracts.

Required formats:

```text
JSON
CSV
Binary
Stats
Diagnostics
```

Rules:

- Grammar-specific code must not invent a different JSON shape.
- Grammar-specific code must not invent a different binary schema.
- Rule names come directly from the Tree-sitter grammar.
- `include_rules` exact matching must work the same for every grammar.
- Field selection must work the same for every grammar.
- Diagnostics must use the same top-level and per-node field names.

## Rule Contract

Status: `Stable`

FastParse does not normalize grammar rule names.

Rules:

- Rule names are the Tree-sitter named node types.
- Rule names are exact and case-sensitive.
- Callers discover rules through exploration mode.
- Production callers should filter to only the needed rules.
- Grammar packages should document common rules but must not hide the raw rule names.

Required docs per grammar:

```text
docs/rules.md or extension README section:
- root/program node
- declarations
- functions/procedures/paragraphs
- calls/references
- comments
- literals
- known ERROR-prone areas
```

## Position And Text Contract

Status: `Stable`

Every grammar must preserve FastParse position semantics.

Rules:

- `text` is the source slice seen by Tree-sitter after selected in-memory normalization.
- `startLine` and `endLine` are 1-based.
- `startColumn` and `endColumn` are 0-based Tree-sitter byte columns.
- `startByte` and `endByte` are 0-based byte offsets.
- `endByte` is exclusive.
- Columns are byte-oriented, not Unicode grapheme counts.

For normalized legacy languages, byte ranges are relative to the normalized in-memory source. Use `normalization = none` when callers need byte-for-byte original offsets.

## Normalization Contract

Status: `Preview`

Normalization is language-specific cleanup applied in RAM before Tree-sitter parses the source.

Rules:

- Normalization must be deterministic.
- Normalization must be memory-only.
- Normalization must not write the normalized source to disk.
- Normalization must not silently remove valid program text.
- Normalization must be documented in the grammar manifest.
- Callers must be able to disable it with `normalization = none`.

Current supported modes:

```text
auto_safe
none
cobol_fixed_legacy
```

For modern languages, `auto_safe` should leave bytes unchanged unless a conservative language-specific cleanup is explicitly documented.

## Diagnostics And Grammar Quality

Status: `Stable` for diagnostics fields; `Preview` for quality thresholds.

Every grammar must be evaluated with diagnostics.

Diagnostics are parse-quality signals, not native failures.

Required metrics:

```text
files_scanned
files_parsed_ok
files_failed_native
files_with_errors
total_lines
total_named_nodes
error_node_count
missing_node_count
error_byte_count
elapsed_seconds
avg_ms_per_file
lines_per_second
```

Recommended quality queries:

```text
top_error_parent_rules
top_error_text_samples
error_nodes_per_kloc
missing_nodes_per_kloc
slowest_files
largest_files
```

Rules:

- A file can parse successfully and still report `hasErrors = true`.
- A grammar can be preview even if it reports errors on real-world source.
- Promotion to stable requires a documented baseline against a representative corpus.
- Multiple grammars for the same language may compete by diagnostics quality.

## Corpus Standard

Status: `Preview`

Every official grammar needs a corpus strategy.

Minimum required corpus:

- One tiny valid smoke sample.
- One intentionally broken sample for diagnostics.
- One sample with comments.
- One sample with Unicode or non-UTF-8 bytes when relevant.
- One large real-world sample when available.

For enterprise legacy languages, maintainers should also track:

- Fixed-format and free-format variants.
- Files with column-sensitive syntax.
- Files with transport/editor trailers.
- Vendor dialects.
- Known parser hang candidates.

Corpus data may remain private, but summary metrics should be publishable.

## Performance Standard

Status: `Preview`

Every grammar package should publish realistic performance numbers.

Minimum benchmark modes:

```text
Stats
Diagnostics
Binary all fields
Binary selected rules/fields
JSON all fields
```

Rules:

- Benchmarks must state hardware, OS, thread count, file count, and total lines.
- Full AST output is expected to be slower than diagnostics.
- Binary output is preferred for high-throughput structured processing.
- Benchmarks should separate file reading, parsing, decoding, and database writing when possible.

## Threading Contract

Status: `Stable`

Grammar extensions must follow the FastParse concurrency contract.

Rules:

- Load language extensions before starting parse worker threads.
- Parse calls may run concurrently after the language is loaded.
- The extension descriptor and Tree-sitter language function must be safe for repeated calls.
- Grammar code must not store per-parse mutable global state.
- Parent applications own queues, file I/O, and database writes.

## Packaging Standard

Status: `Preview`

Every official grammar should be installable through package managers.

NuGet:

```text
FastParser.Language.Cobol
runtimes/linux-x64/native/libfastparse_language_cobol.so
runtimes/osx-arm64/native/libfastparse_language_cobol.dylib
runtimes/osx-x64/native/libfastparse_language_cobol.dylib
runtimes/win-x64/native/fastparse_language_cobol.dll
```

PyPI:

```text
fastparse-language-cobol
fastparse_language_cobol/
  manifest.json
  native/
```

crates.io:

```text
fastparse-language-cobol
```

Maven:

```text
io.fastparser:fastparser-language-cobol
```

Package-manager installs should be enough for normal users. Explicit path loading remains available for local builds and enterprise deployments.

## Validation Checklist

Status: `Stable`

Before publishing a grammar package:

- Build native extension on Linux x64.
- Build native extension on macOS arm64.
- Build native extension on macOS x64.
- Build native extension on Windows x64.
- Load extension by explicit path.
- Verify `language_available(canonical_name)`.
- Parse smoke sample as JSON.
- Parse smoke sample as Binary and decode in at least one binding.
- Parse broken sample as Diagnostics and confirm `hasErrors = true`.
- Run a threaded parse smoke test.
- Run package validation from a clean consumer.
- Attach release assets and checksums.
- Publish through trusted/OIDC flow where available.
- Run public-registry post-publish smoke tests.

## AI-Agent Contract

Status: `Stable`

When an AI agent adds or uses a grammar:

- Install the core package and the language package through the host package manager.
- Load bundled languages before parsing.
- Use explicit path loading only for local builds or diagnostics.
- Use Diagnostics for first-pass grammar quality scans.
- Use Binary for high-throughput structured extraction.
- Use JSON for exploration and debugging.
- Request only needed rules and fields in production.
- Keep SQLite, files, queues, and reports in the parent application.
- Do not depend on internal Tree-sitter build paths.
- Do not assume a grammar is error-free just because the native call succeeded.

## COBOL First Implementation Target

Status: `Preview`

COBOL should be the first official grammar extension that proves this standard.

Minimum target:

- Canonical language: `cobol`.
- Package names:
  - `FastParser.Language.Cobol`
  - `fastparse-language-cobol`
  - `fastparse-language-cobol` for crates.io
  - `io.fastparser:fastparser-language-cobol`
- Dynamic library names:
  - `libfastparse_language_cobol.so`
  - `libfastparse_language_cobol.dylib`
  - `fastparse_language_cobol.dll`
- Descriptor symbol: `fastparse_language_extension_descriptor`.
- Default normalization: `auto_safe`.
- Supported normalization: `auto_safe`, `none`, `cobol_fixed_legacy`.
- Required validation corpus: private enterprise COBOL inventory plus public smoke samples.
- Required quality output: diagnostics summary over the large corpus.

COBOL preview can ship with known grammar errors if those errors are measured, documented, and do not cause native crashes or hangs.
