# FastParse PL/SQL Extension

This extension registers the promoted `tree-sitter-plsql` grammar as the FastParse language `plsql`.

The extension follows the FastParse language-extension standard:

- Native descriptor: `fastparse_language_extension_descriptor`
- Tree-sitter symbol: `tree_sitter_plsql`
- Canonical language: `plsql`
- Package names: `fastparse-language-plsql`, `FastParser.Language.Plsql`

## Build

From the repository root:

```sh
python3 scripts/package_language_extension.py --language plsql --version 0.1.5
```

The promoted grammar is expected at:

```text
grammars/tree-sitter-plsql
```

The local extension library is emitted to:

```text
bin/libfastparse_language_plsql.dylib
```

On Linux the extension suffix is `.so`; on Windows it is `.dll`.

## Package

NuGet packaging uses the native archives produced per platform:

```sh
python3 scripts/package_nuget_language_extension.py \
  --language plsql \
  --version 0.1.5 \
  --core-version 0.1.4 \
  --archive dist/languages/fastparse-language-plsql-0.1.5-macos-arm64.tar.gz
```

## CI and release

- `.github/workflows/plsql-extension-ci.yml` builds only the PL/SQL language extension and runs a FastParse smoke test.
- `.github/workflows/publish-plsql-nuget.yml` builds the PL/SQL native assets for Linux, macOS arm64, macOS x64, and Windows, validates `FastParser.Language.Plsql`, optionally publishes it to NuGet, then runs published-package smoke tests.

Use the `plsql-v<version>` tag only for PL/SQL language package releases. The workflow pins the dependency to the already published `FastParser` core version unless overridden from manual dispatch.
