# tree-sitter-java-frameworks

Java-derived grammar for detecting framework usage as syntax nodes.

This grammar is forked from the local productive Java grammar and is maintained as the official/common framework-detection grammar. Client-specific profiles should live in separate extension grammars.

## Scope

The grammar starts as a clean Java baseline. Framework-specific rules should be added one cataloged rule at a time under `docs/rule-catalogs/`.

Implemented catalogs:

- `framework_usage_evidence.md`: safe framework evidence through imports, annotations, and JDBC URL literals.
- `framework_query_families.md`: family-level query captures for framework imports, annotations, calls, constructors, and literals.
- `framework_support_matrix.md`: final support matrix by framework family, public corpus coverage, negative contract, and stable-release gate.

Validation workflow:

- `validation.md`: reusable validation commands, encoding normalization, query audit, and cleanup policy.

Client-specific framework catalogs should be kept separate from official/common framework catalogs.

Method and constructor framework detections live in `queries/frameworks.scm` unless they can be promoted into grammar rules without reserving normal Java identifiers.
