# Java Frameworks Extension Release Validation

Date: 2026-06-30

## Local Artifacts

Generated and validated on macOS arm64:

```text
dist/languages/fastparse-language-java-frameworks-0.1.0-preview.25-macos-arm64.tar.gz
dist/python/fastparse-0.1.0rc25-py3-none-macosx_15_0_arm64.whl
dist/python-languages/fastparse_language_java_frameworks-0.1.0rc25-py3-none-macosx_11_0_arm64.whl
dist/nuget/FastParser.0.1.0-preview.25.nupkg
dist/nuget-languages/FastParser.Language.JavaFrameworks.0.1.0-preview.25.nupkg
```

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
- dependency metadata: `fastparse==0.1.0rc25`

The NuGet package includes:

- `runtimes/osx-arm64/native/libfastparse_language_java_frameworks.dylib`
- `contentFiles/any/any/fastparse/languages/java-frameworks/manifest.json`
- `contentFiles/any/any/fastparse/languages/java-frameworks/queries/frameworks.scm`
- `buildTransitive/FastParser.Language.JavaFrameworks.targets`

## Local Smoke Tests

Python clean install:

```text
python3 scripts/validate_python_language_wheel.py \
  dist/python/fastparse-0.1.0rc25-py3-none-macosx_15_0_arm64.whl \
  dist/python-languages/fastparse_language_java_frameworks-0.1.0rc25-py3-none-macosx_11_0_arm64.whl \
  --language java-frameworks
```

Result: OK.

Python dependency-only install:

```text
pip install --no-index --find-links dist/python --find-links dist/python-languages fastparse-language-java-frameworks==0.1.0rc25
```

Result: OK. The extension pulled `fastparse==0.1.0rc25` and loaded with `load_bundled_language("java-frameworks")`.

NuGet clean consumer:

```text
python3 scripts/validate_nuget_language_package.py \
  --core-package dist/nuget/FastParser.0.1.0-preview.25.nupkg \
  --language-package dist/nuget-languages/FastParser.Language.JavaFrameworks.0.1.0-preview.25.nupkg \
  --version 0.1.0-preview.25 \
  --language java-frameworks
```

Result: OK.

## Publication Status

Ready for registry publication through `.github/workflows/release.yml`.

The release workflow now builds, validates, publishes when enabled, and runs post-publish smoke tests for:

- `fastparse-language-java-frameworks`
- `FastParser.Language.JavaFrameworks`

Not published from this machine because public publishing must happen from the trusted GitHub Actions workflow and requires:

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
