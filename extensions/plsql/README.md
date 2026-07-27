# FastParse PL/SQL Extension

FastParse language extension for the public `tree-sitter-plsql` grammar.

The canonical FastParse language name is `plsql`. The native descriptor exports
`tree_sitter_plsql` and is built as `libfastparse_language_plsql`.

Configure a local grammar checkout when generating the build:

```sh
cmake -S . -B build-plsql-extension \
  -DFASTPARSE_PLSQL_GRAMMAR_DIR=/path/to/tree-sitter-plsql
cmake --build build-plsql-extension --target fastparse_language_plsql
```

The current grammar covers pure Oracle PL/SQL, SQL, and DDL. Converted Oracle
Forms exports remain outside its declared scope.
