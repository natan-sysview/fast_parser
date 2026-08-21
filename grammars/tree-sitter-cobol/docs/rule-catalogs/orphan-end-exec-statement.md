# Orphan END-EXEC Statement

## Rule Name

`orphan_end_exec_statement`

## Purpose

Tolerate a standalone unmatched `END-EXEC` that appears as legacy source text in procedure code, without changing balanced embedded `EXEC SQL ... END-EXEC` or `EXEC CICS ... END-EXEC` parsing.

## Included Forms

```cobol
MOVE WS-PROD TO PROD-CVE-PRODUCTO.
END-EXEC
PERFORM 2215-VERIFICA-PRODUCTO.
```

## Excluded Forms

- Treating `END-EXEC` as a generic `_end_statement`.
- Changing balanced embedded SQL/CICS blocks.
- Inferring a missing opening `EXEC` block.

## Implementation Boundary

The rule is added only as a regular `_statement` alternative. A previous candidate that added `_END_EXEC` to `_end_statement` was rejected because it competed with normal embedded blocks and caused a large full-inventory regression.

## Corpus Examples

- `orphan end exec as statement`
- `balanced exec sql remains exec sql statement`

## Validation Plan

- Generate parser.
- Run `orphan_end_exec_statement.txt`.
- Run full corpus.
- Smoke parse `CG2C0340`.
- Validate full inventory and require `MISSING` nodes to reach 0 without increasing `ERROR` nodes or files.

## Validation Result

Candidate: `current_orphan_end_exec_statement_20260814`

- Corpus: 197/197
- Inventory files: 74,242
- Parsed OK: 74,242
- Hard failures: 0
- Files with `ERROR`: 2,337 -> 2,334
- `ERROR` nodes: 2,971 -> 2,969
- Files with `MISSING`: 1 -> 0
- `MISSING` nodes: 1 -> 0
- Changed files: 3
- Regressed files: 0

Decision: stable.
