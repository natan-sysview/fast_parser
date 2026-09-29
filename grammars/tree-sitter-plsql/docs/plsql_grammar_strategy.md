# PL/SQL Grammar Strategy

This experimental grammar is the repair workspace for Oracle PL/SQL and Oracle SQL DDL/DML parsing.

## Current Scope

The initial inventory classifies PL/SQL sources into these subtypes:

```text
PKB package bodies
PKS package specs
PRC procedures
FNC functions
CR  CREATE TABLE scripts
```

The shared SQLite inventory keeps these rows in `files` with `type = 'plsql'` and the source project in `project_name`.

## Initial Known Failures

The copied upstream grammar can generate successfully, but the initial smoke checks show important gaps:

- `CREATE TABLE ...` currently produces `ERROR` nodes.
- `CREATE OR REPLACE PROCEDURE ...` currently produces `ERROR` nodes.
- SQL*Plus `/` statement separators are not handled cleanly.
- The inherited `corpus/test.txt` is not a useful PL/SQL corpus for modern Tree-sitter CLI workflows.

## Repair Order

Start with one subtype at a time:

```text
CR -> PKS -> PKB -> PRC -> FNC
```

For each subtype, add:

- A catalog under `docs/rule-catalogs/`.
- Positive and negative corpus tests under `test/corpus/`.
- A before/after baseline.
- Full inventory validation with error and missing-node counts.

Do not promote changes back to `grammars/tree-sitter-plsql` until corpus tests pass and inventory validation is understood.
