# tree-sitter-java-frameworks

Experimental Java-derived grammar for detecting framework usage as syntax nodes.

This grammar is forked from the local productive Java grammar and should be evolved in the experimental grammar area before promotion.

## Scope

The grammar starts as a clean Java baseline. Framework-specific rules should be added one cataloged rule at a time under `docs/rule-catalogs/`.

Implemented catalogs:

- `framework_usage_evidence.md`: safe framework evidence through imports, annotations, and JDBC URL literals.
- `framework_query_families.md`: family-level query captures for framework imports, annotations, calls, constructors, and literals.

Validation workflow:

- `validation.md`: reusable validation commands, encoding normalization, query audit, and cleanup policy.

Client-specific framework catalogs should be kept separate from official/common framework catalogs.

Method and constructor framework detections live in `queries/frameworks.scm` unless they can be promoted into grammar rules without reserving normal Java identifiers.
