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

The preferred long-term distribution model is core plus optional language extension packages. See [Language Extensions](language_extensions.md) and [FastParse Grammar Standard](grammar_standard.md).

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

That validation extracts the archive, checks the public layout, validates `manifest.json`, loads the native library through the Python binding, parses Java source as JSON, binary MessagePack, and stats, compiles and runs the packaged C example, builds and runs the packaged C# example, and runs the packaged `smoke_test.py`. macOS and Linux also run the packaged Python example. This catches packaging errors that normal source-tree tests can miss.

Each archive includes:

```text
manifest.json    Machine-readable package metadata.
GETTING_STARTED.md Quick start for humans and AI agents.
smoke_test.py    End-user smoke test for the unpacked package.
RELEASE.md       Human-readable package summary.
examples/c/      Minimal C example compiled during package validation.
examples/csharp/ Minimal C# example built and run during package validation.
```

Tagged releases also attach `SHA256SUMS.txt`, generated from the final archives in the release job.

This avoids many cross-compiling edge cases around platform linkers, dynamic library naming, exported symbols, and runtime testing.

## NuGet Package

The release workflow also builds a C# NuGet package artifact:

```text
FastParser.<version>.nupkg
```

The package contains the managed C# binding plus the native libraries from the release archives:

```text
AI_AGENT_GUIDE.md
fastparser-icon.png
docs/
examples/csharp/01_parse_string/
examples/csharp/02_binary_decode/
examples/csharp/nuget/01_parse_string/
examples/csharp/nuget/02_binary_decode/
lib/net8.0/FastParse.dll
lib/net9.0/FastParse.dll
runtimes/linux-x64/native/libfastparse.so
runtimes/osx-arm64/native/libfastparse.dylib
runtimes/osx-x64/native/libfastparse.dylib
runtimes/win-x64/native/fastparse.dll
```

Build it locally from an existing GitHub release:

```bash
python3 scripts/package_nuget.py \
  --version 0.1.0-preview.17 \
  --release-tag v0.1.0-preview.17
```

Validate it from a clean consumer project:

```bash
python3 scripts/validate_nuget_package.py dist/nuget/FastParser.0.1.0-preview.17.nupkg
```

Install from the local package directory:

```bash
dotnet add package FastParser \
  --version 0.1.0-preview.17 \
  --source dist/nuget
```

Publishing to nuget.org uses NuGet Trusted Publishing from GitHub Actions. The public NuGet package ID is `FastParser`; the C# namespace remains `FastParse`.

Tagged NuGet releases also run a post-publish smoke test from nuget.org on Linux x64, Windows x64, macOS arm64, and macOS x64.

## NuGet Language Extension Packages

Optional parse languages are packaged separately from the core `FastParser` package. The first pilot package is:

```text
FastParser.Language.Python
```

The package contains only language-extension assets:

```text
contentFiles/any/any/fastparse/languages/python/manifest.json
buildTransitive/FastParser.Language.Python.targets
runtimes/linux-x64/native/libfastparse_language_python.so
runtimes/osx-arm64/native/libfastparse_language_python.dylib
runtimes/osx-x64/native/libfastparse_language_python.dylib
runtimes/win-x64/native/fastparse_language_python.dll
```

Build from language archives:

```bash
python3 scripts/package_nuget_language_extension.py \
  --language python \
  --version 0.1.0-preview.17 \
  --archive dist/languages/fastparse-language-python-0.1.0-preview.17-linux-x64.tar.gz \
  --archive dist/languages/fastparse-language-python-0.1.0-preview.17-macos-arm64.tar.gz \
  --archive dist/languages/fastparse-language-python-0.1.0-preview.17-macos-x64.tar.gz \
  --archive dist/languages/fastparse-language-python-0.1.0-preview.17-windows-x64.zip
```

Publishing is gated by:

```text
NUGET_LANGUAGE_PYTHON_PUBLISH=true
```

## Python Wheel / PyPI Package

The release workflow also builds Python wheels for:

```text
manylinux2014_x86_64
macosx_10_15_x86_64
macosx_11_0_arm64
win_amd64
```

The public PyPI package name is:

```text
fastparse
```

Python package versions must use PEP 440. Preview release names are converted before publishing:

| FastParse release | PyPI version |
|---|---|
| `0.1.0-preview.17` | `0.1.0rc17` |

Each wheel includes:

```text
fastparse/
fastparse/py.typed
tsmp/
tsmp/py.typed
fastparse/native/<platform native library>
```

Normal Python consumers install and import without manually configuring native paths:

```bash
pip install fastparse
```

```python
from fastparse import FastParse
```

Build a local wheel:

```bash
python3 scripts/package_python_wheel.py \
  --version 0.1.0-preview.17
```

Validate a wheel in a clean virtual environment:

```bash
python3 scripts/validate_python_wheel.py \
  dist/python/fastparse-0.1.0rc17-py3-none-macosx_11_0_arm64.whl
```

Tagged releases build wheels in GitHub Actions and upload them as artifacts. Publishing to PyPI is gated by the repository variable:

```text
PYPI_PUBLISH=true
```

PyPI should be configured with Trusted Publishing for:

```text
owner: natan-sysview
repository: fast_parser
workflow: release.yml
project: fastparse
```

Tagged PyPI releases also run a post-publish smoke test from pypi.org on Linux x64, Windows x64, macOS arm64, and macOS x64. The smoke test installs the exact published package in a clean virtual environment, loads the bundled native library, parses Java as JSON, checks binary output, decodes binary output, and checks diagnostics output.

## PyPI Language Extension Wheels

Optional parse languages are packaged as separate wheels. The first pilot package is:

```text
fastparse-language-python
```

Each wheel contains one native language extension for the platform tag:

```text
fastparse_language_python/
fastparse_language_python/manifest.json
fastparse_language_python/py.typed
fastparse_language_python/native/osx-arm64/libfastparse_language_python.dylib
```

Build locally:

```bash
python3 scripts/package_python_language_wheel.py \
  --language python \
  --version 0.1.0-preview.17
```

Validate with a core wheel:

```bash
python3 scripts/validate_python_language_wheel.py \
  dist/python/fastparse-0.1.0rc17-py3-none-macosx_11_0_arm64.whl \
  dist/python-languages/fastparse_language_python-0.1.0rc17-py3-none-macosx_11_0_arm64.whl
```

Publishing is gated by:

```text
PYPI_LANGUAGE_PYTHON_PUBLISH=true
```

The workflow lives at:

```text
.github/workflows/release.yml
```

It can run manually with a version:

```text
workflow_dispatch -> version = 0.1.0-preview.17
```

Or automatically on tags:

```bash
git tag v0.1.0-preview.17
git push origin v0.1.0-preview.17
```

For tags, the workflow attaches generated archives to the GitHub Release.

## Local Release Package

Create a local package for the current platform:

```bash
python3 scripts/package_release.py --version 0.1.0-preview.17
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
