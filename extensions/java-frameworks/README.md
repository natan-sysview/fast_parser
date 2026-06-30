# FastParse Java Frameworks Extension

Local FastParse language extension for the promoted `tree-sitter-java-frameworks` grammar.

The extension intentionally uses the canonical language name `java-frameworks` so it can coexist with FastParse's built-in `java` language. The native descriptor exposes `tree_sitter_java_frameworks`; framework evidence queries are distributed under `queries/frameworks.scm`.

The grammar source is expected at `grammars/tree-sitter-java-frameworks` for formal local builds.
