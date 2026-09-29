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
python3 scripts/package_language_extension.py --language plsql --version 0.1.3
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
  --version 0.1.3 \
  --core-version 0.1.3 \
  --archive dist/languages/fastparse-language-plsql-0.1.3-macos-arm64.tar.gz
```
