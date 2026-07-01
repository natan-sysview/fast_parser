# JavaSwing Extension Release

## Package Names

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

## Public Publication Requirements

Before publishing publicly:

- Use `.github/workflows/release.yml` so all native extension RIDs are built: `linux-x64`, `osx-arm64`, `osx-x64`, `win-x64`.
- Build a matching core FastParse package for the same version.
- Configure NuGet trusted publishing for `FastParser.Language.JavaSwing`.
- Enable `NUGET_LANGUAGE_JAVASWING_PUBLISH=true`.
- Run post-publish smoke tests from nuget.org.

## Runtime Contract

- Load with `parser.LoadBundledLanguage("javaswing")` in C#.
- Query asset is bundled as `queries/swing.scm`.
- Parse/query calls receive source bytes or strings in memory; the extension does not read source files.
- Use one parser/client per worker and load language extensions before starting high-volume worker threads.
