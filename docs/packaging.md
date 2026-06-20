# Packaging Strategy

FastParse should be distributed as a small native library plus one public C header.

The package should be easy to load from Python, C#, Rust, Java, Node, Go, or any runtime that can call a C ABI.

## Package Contents

Recommended runtime package:

```text
include/fastparse.h
include/tsmp.h         compatibility
lib/libfastparse.dylib macOS
lib/libfastparse.so    Linux
bin/fastparse.dll      Windows
LICENSES/
README.md
docs/
examples/
```

The package should not include:

```text
node_modules/
venv/
grammar test suites/
object files/
local benchmark outputs/
temporary generated files/
```

## Naming

Use `fastparse` as the stable public name.

Recommended native artifact names:

```text
macOS   libfastparse.dylib
Linux   libfastparse.so
Windows fastparse.dll
```

Older lab builds emitted:

```text
bin/libts_multi_parser.dylib
bin/libtsmp.dylib
```

Those names are legacy. New builds should emit `fastparse`.

## Versioning

There are three versions to track:

| Version | Meaning |
|---|---|
| ABI version | Compatibility of `include/tsmp.h` and exported symbols. |
| Package version | Release version of TSMP artifacts. |
| Grammar versions | Exact Tree-sitter grammar revisions included in the build. |

The runtime function:

```c
const char *tsmp_version(void);
```

should report the TSMP package/API version. Grammar versions should be documented in release metadata.

## ABI Stability

The binding surface should remain intentionally small:

```text
tsmp_version
tsmp_parse
tsmp_result_free
```

FastParse-branded symbols are preferred:

```text
fastparse_version
fastparse_parse
fastparse_result_free
```

Rules for ABI changes:

- Do not reorder existing struct fields.
- Do not change enum integer values.
- Do not remove exported functions.
- Add new fields only after planning ABI compatibility.
- Prefer adding a new options/result version if the ABI needs to grow significantly.

## Memory Ownership

All returned native memory must be released with:

```c
tsmp_result_free(&result);
```

Bindings should hide this from normal users with `try/finally`, `defer`, `Drop`, `IDisposable`, or equivalent runtime cleanup.

## Language Profiles

Package size should be controlled with language profiles.

Possible profiles:

```text
tsmp-java       Java only
tsmp-jvm        Java + C#
tsmp-corelangs  Java + C# + Rust + Python
tsmp-full       All supported grammars
```

Each profile should expose the same C ABI. The only difference is which `options.language` values are supported.

Unsupported languages return:

```text
TSMP_ERROR_UNSUPPORTED_LANGUAGE
```

## Binding Packages

Recommended binding packages:

| Language | Package contents |
|---|---|
| Python | ctypes/cffi wrapper plus platform native libraries. |
| C# | P/Invoke wrapper plus RID-specific native assets. |
| Rust | `extern "C"` wrapper plus safe Rust facade. |

The binding layer should own:

- Loading the correct dynamic library.
- Converting user-friendly options into `TsmpOptions`.
- Freeing `TsmpResult`.
- Presenting bytes/string results naturally for that language.

The binding layer should not reimplement parsing, AST traversal, or rule filtering.

## Release Validation

Every package should pass:

```text
build shared library
run C smoke test
run Python contract tests
validate exported symbols
parse empty source
parse non-ASCII byte sample
parse selected real corpus samples
```

For macOS/Linux, exported symbol validation can use `nm`.

For Windows, use `dumpbin` or an equivalent symbol inspection tool.

Expected public symbols:

```text
fastparse_version
fastparse_parse
fastparse_result_free
tsmp_version
tsmp_parse
tsmp_result_free
```

## GitHub Actions Native Artifacts

The recommended first release strategy is multi-runner builds, not a single cross-compiling job.

GitHub-hosted runners can build native artifacts on their target operating systems:

| Runner | Artifact |
|---|---|
| `ubuntu-latest` | `fastparse-<version>-linux-x64.tar.gz` |
| `macos-15-intel` | `fastparse-<version>-macos-x64.tar.gz` |
| `macos-14` | `fastparse-<version>-macos-arm64.tar.gz` |
| `windows-latest` | `fastparse-<version>-windows-x64.zip` |

Each package job also validates the generated archive:

```bash
python scripts/validate_release_package.py <archive> --platform <platform>
```

That validation extracts the archive, checks the public layout, loads the native library through the Python binding, and parses Java source as JSON, binary MessagePack, and stats. macOS and Linux also run the packaged Python example. This catches packaging errors that normal source-tree tests can miss.

This avoids many cross-compiling edge cases around platform linkers, dynamic library naming, exported symbols, and runtime testing.

The workflow lives at:

```text
.github/workflows/release.yml
```

It can run manually with a version:

```text
workflow_dispatch -> version = 0.1.0-preview
```

Or automatically on tags:

```bash
git tag v0.1.0-preview
git push origin v0.1.0-preview
```

For tags, the workflow attaches generated archives to the GitHub Release.

## Local Release Package

Create a local package for the current platform:

```bash
python3 scripts/package_release.py --version 0.1.0-preview
```

After building, the package appears under:

```text
dist/
```

Package contents:

```text
lib/ or bin/ native library
include/
bindings/
examples/
docs/
README.md
LICENSE
NOTICE
THIRD_PARTY_NOTICES.md
CHANGELOG.md
RELEASE.md
```

## Open Decisions

- Whether to ship one package per language profile or one package with multiple downloadable variants.
- Whether to include static libraries.
- Whether bindings should bundle native libraries or require users to install the TSMP runtime separately.
- Whether release archives should include source grammar metadata as JSON.
