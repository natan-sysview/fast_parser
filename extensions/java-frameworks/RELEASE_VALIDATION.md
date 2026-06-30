# Java Frameworks Extension Release Validation

Date: 2026-06-30

## Local Artifacts

Generated and validated on macOS arm64 for the stable release candidate:

```text
dist/languages/fastparse-language-java-frameworks-0.1.0-macos-arm64.tar.gz
dist/python/fastparse-0.1.0-py3-none-macosx_11_0_arm64.whl
dist/python-languages/fastparse_language_java_frameworks-0.1.0-py3-none-macosx_11_0_arm64.whl
dist/nuget-languages/FastParser.Language.JavaFrameworks.0.1.0.nupkg
```

The core NuGet package is validated by CI because `scripts/package_nuget.py` intentionally requires all native RIDs (`linux-x64`, `osx-arm64`, `osx-x64`, `win-x64`).

## Package Contents Verified

The native archive includes:

- `native/osx-arm64/libfastparse_language_java_frameworks.dylib`
- `manifest.json`
- `queries/frameworks.scm`
- grammar metadata under `grammar/`

The PyPI wheel includes:

- `fastparse_language_java_frameworks/native/osx-arm64/libfastparse_language_java_frameworks.dylib`
- `fastparse_language_java_frameworks/manifest.json`
- `fastparse_language_java_frameworks/queries/frameworks.scm`
- dependency metadata: `fastparse==0.1.0`

The NuGet package includes:

- `runtimes/osx-arm64/native/libfastparse_language_java_frameworks.dylib`
- `contentFiles/any/any/fastparse/languages/java-frameworks/manifest.json`
- `contentFiles/any/any/fastparse/languages/java-frameworks/queries/frameworks.scm`
- `buildTransitive/FastParser.Language.JavaFrameworks.targets`

## Local Smoke Tests

Python clean install:

```text
python3 scripts/validate_python_language_wheel.py \
  dist/python/fastparse-0.1.0-py3-none-macosx_11_0_arm64.whl \
  dist/python-languages/fastparse_language_java_frameworks-0.1.0-py3-none-macosx_11_0_arm64.whl \
  --language java-frameworks
```

Result: OK.

Python dependency-only install:

```text
pip install --no-index --find-links dist/python --find-links dist/python-languages fastparse-language-java-frameworks==0.1.0
```

Result: OK. The extension pulled `fastparse==0.1.0` and loaded with `load_bundled_language("java-frameworks")`.

NuGet package structure:

```text
python3 scripts/package_nuget_language_extension.py \
  --language java-frameworks \
  --version 0.1.0 \
  --core-version 0.1.0 \
  --archive dist/languages/fastparse-language-java-frameworks-0.1.0-macos-arm64.tar.gz \
  --output-dir dist/nuget-languages
```

Result: OK. The package contains stable manifest metadata, `queries/frameworks.scm`, `buildTransitive/FastParser.Language.JavaFrameworks.targets`, Apache 2.0 license URL metadata, and a `FastParser` dependency pinned to `0.1.0`.

Full NuGet clean-consumer validation is deferred to GitHub Actions for the stable tag because the local machine has only the macOS arm64 native archive.

## Publication Status

`0.1.0-preview.32` was published through `.github/workflows/release.yml` and passed public registry smoke tests.

The release workflow now builds, validates, publishes when enabled, and runs post-publish smoke tests for:

- `fastparse-language-java-frameworks`
- `FastParser.Language.JavaFrameworks`

Stable `0.1.0` uses the same release workflow and package layout, with final corpus/docs hardening from `framework_support_matrix.md`.

Local stable gate status:

- `tree-sitter test`: 5/5 passed.
- `tree-sitter query queries/frameworks.scm`: passed on a synthetic framework smoke file.
- C native `ctest`: 2/2 passed after building all test targets.
- Python contract tests: 33 run, 30 passed, 3 skipped for unrelated optional extensions not built locally.
- C# contract tests: 17/17 passed.
- `npm pack --dry-run`: passed for `tree-sitter-java-frameworks`.
- `cargo package --allow-dirty --no-verify`: passed for `tree-sitter-java-frameworks`.
- Stable Python language wheel validation: passed.
- Stable NuGet language package structure validation: passed.

Public publishing must happen from the trusted GitHub Actions workflow and requires:

- PyPI trusted publisher or token for `fastparse-language-java-frameworks`.
- NuGet trusted publishing policy or token for `FastParser.Language.JavaFrameworks`.
- Native extension assets for `linux-x64`, `osx-arm64`, `osx-x64`, and `win-x64`.
- Matching core FastParse packages for the same version on PyPI/NuGet.

## Scripts Updated

- `scripts/package_language_extension.py`
- `scripts/package_python_language_wheel.py`
- `scripts/package_nuget_language_extension.py`
- `scripts/validate_python_language_wheel.py`
- `scripts/validate_nuget_language_package.py`
- `scripts/validate_published_pypi_language.py`
- `scripts/validate_published_nuget_language.py`
- `.github/workflows/release.yml`

## Docs Updated

- `extensions/java-frameworks/RELEASE.md`
- `docs/package_registry_setup.md`
- `docs/release_checklist.md`
