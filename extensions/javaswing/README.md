# FastParse JavaSwing Extension

FastParse language extension for the public `tree-sitter-javaswing` grammar.

The extension uses the canonical FastParse language name `javaswing` so it can coexist with FastParse's built-in `java` language and with the broader `java-frameworks` extension. The native descriptor exposes `tree_sitter_javaswing`; Swing evidence queries are distributed under `queries/swing.scm`.

The grammar source is vendored at `grammars/tree-sitter-javaswing` for release builds.
