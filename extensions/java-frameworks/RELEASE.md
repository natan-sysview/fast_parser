# Java Frameworks Extension Release

## Package Names

- PyPI: `fastparse-language-java-frameworks`
- Python import: `fastparse_language_java_frameworks`
- NuGet: `FastParser.Language.JavaFrameworks`
- FastParse language: `java-frameworks`
- Native symbol/file stem: `java_frameworks`

## Local Build

From the lab root:

```sh
python3 scripts/package_language_extension.py \
  --language java-frameworks \
  --version 0.1.0-preview.30 \
  --dist-dir dist/languages

python3 scripts/package_python_language_wheel.py \
  --language java-frameworks \
  --version 0.1.0-preview.30 \
  --output-dir dist/python-languages

python3 scripts/package_nuget_language_extension.py \
  --language java-frameworks \
  --version 0.1.0-preview.30 \
  --core-version 0.1.0-preview.30 \
  --archive dist/languages/fastparse-language-java-frameworks-0.1.0-preview.30-macos-arm64.tar.gz \
  --output-dir dist/nuget-languages
```

Local macOS arm64 artifacts:

```text
dist/languages/fastparse-language-java-frameworks-0.1.0-preview.30-macos-arm64.tar.gz
dist/python-languages/fastparse_language_java_frameworks-0.1.0rc30-py3-none-macosx_11_0_arm64.whl
dist/nuget-languages/FastParser.Language.JavaFrameworks.0.1.0-preview.30.nupkg
```

## Local Validation

```sh
python3 scripts/validate_python_language_wheel.py \
  dist/python/fastparse-0.1.0rc30-py3-none-macosx_15_0_arm64.whl \
  dist/python-languages/fastparse_language_java_frameworks-0.1.0rc30-py3-none-macosx_11_0_arm64.whl \
  --language java-frameworks

python3 scripts/validate_nuget_language_package.py \
  --core-package dist/nuget/FastParser.0.1.0-preview.30.nupkg \
  --language-package dist/nuget-languages/FastParser.Language.JavaFrameworks.0.1.0-preview.30.nupkg \
  --version 0.1.0-preview.30 \
  --language java-frameworks
```

## Public Publication Requirements

Before publishing publicly:

- Use `.github/workflows/release.yml` so all native extension RIDs are built: `linux-x64`, `osx-arm64`, `osx-x64`, `win-x64`.
- Build matching core FastParse packages for the same version.
- Configure PyPI trusted publisher for `fastparse-language-java-frameworks`.
- Configure NuGet trusted publishing for `FastParser.Language.JavaFrameworks`.
- Enable:
  - `PYPI_LANGUAGE_JAVA_FRAMEWORKS_PUBLISH=true`
  - `NUGET_LANGUAGE_JAVA_FRAMEWORKS_PUBLISH=true`
- Run post-publish smoke tests from PyPI and nuget.org.

## Runtime Contract

- Load with `parser.load_bundled_language("java-frameworks")` in Python.
- Load with `parser.LoadBundledLanguage("java-frameworks")` in C#.
- Query asset is bundled as `queries/frameworks.scm`.
- Parse/query calls receive source bytes or strings in memory; the extension does not read source files.
- Use one parser/client per worker and load language extensions before starting high-volume worker threads.
