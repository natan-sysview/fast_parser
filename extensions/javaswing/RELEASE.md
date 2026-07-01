# JavaSwing Extension Release

## Package Names

- PyPI: `fastparse-language-javaswing`
- Python import: `fastparse_language_javaswing`
- NuGet: `FastParser.Language.JavaSwing`
- FastParse language: `javaswing`
- Native symbol/file stem: `javaswing`
- Grammar: `tree-sitter-javaswing`

## Local Build

From the FastParse repo root:

```sh
python3 scripts/package_language_extension.py \
  --language javaswing \
  --version 0.1.0 \
  --dist-dir dist/languages

python3 scripts/package_python_language_wheel.py \
  --language javaswing \
  --version 0.1.0 \
  --output-dir dist/python-languages

python3 scripts/package_nuget_language_extension.py \
  --language javaswing \
  --version 0.1.0 \
  --core-version 0.1.0 \
  --archive dist/languages/fastparse-language-javaswing-0.1.0-macos-arm64.tar.gz \
  --output-dir dist/nuget-languages
```

## Local Validation

```sh
python3 scripts/validate_nuget_language_package.py \
  --core-package dist/nuget/FastParser.0.1.0.nupkg \
  --language-package dist/nuget-languages/FastParser.Language.JavaSwing.0.1.0.nupkg \
  --version 0.1.0 \
  --language javaswing
```

Validate the Python wheel against a published core `fastparse` wheel:

```sh
python3 scripts/validate_python_language_wheel.py \
  dist/python/fastparse-0.1.0-py3-none-macosx_11_0_arm64.whl \
  dist/python-languages/fastparse_language_javaswing-0.1.0-py3-none-macosx_11_0_arm64.whl \
  --language javaswing
```

## Public Publication Requirements

Before publishing publicly:

- Use `.github/workflows/release.yml` so all native extension RIDs are built: `linux-x64`, `osx-arm64`, `osx-x64`, `win-x64`.
- Build a matching core FastParse package for the same version.
- Configure PyPI trusted publisher for `fastparse-language-javaswing`.
- Configure NuGet trusted publishing for `FastParser.Language.JavaSwing`.
- Use `.github/workflows/publish-javaswing-pypi.yml` for PyPI-only publication against an already published core package.
- Use `.github/workflows/publish-javaswing-nuget.yml` for NuGet-only publication against an already published core package.
- Enable `NUGET_LANGUAGE_JAVASWING_PUBLISH=true`.
- Run post-publish smoke tests from nuget.org.

## Runtime Contract

- Load with `parser.LoadBundledLanguage("javaswing")` in C#.
- Load with `parser.load_bundled_language("javaswing")` in Python.
- Query asset is bundled as `queries/swing.scm`.
- Parse/query calls receive source bytes or strings in memory; the extension does not read source files.
- Use one parser/client per worker and load language extensions before starting high-volume worker threads.
