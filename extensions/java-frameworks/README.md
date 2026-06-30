# FastParse Java Frameworks Extension

FastParse language extension for the promoted `tree-sitter-java-frameworks` grammar.

The extension intentionally uses the canonical language name `java-frameworks` so it can coexist with FastParse's built-in `java` language. The native descriptor exposes `tree_sitter_java_frameworks`; framework evidence queries are distributed under `queries/frameworks.scm`.

The grammar source is expected at `grammars/tree-sitter-java-frameworks` for formal local builds.

Current package status: stable first release candidate for FastParse `0.1.0`.

Support matrix: `grammars/tree-sitter-java-frameworks/docs/rule-catalogs/framework_support_matrix.md`.
