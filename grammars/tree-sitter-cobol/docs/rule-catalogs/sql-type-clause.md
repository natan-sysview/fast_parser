# Rule Catalog: SQL TYPE Clause

Status: implemented in experimental grammar.

## Goal

Parse DB2 host-variable data descriptions that use COBOL `USAGE IS SQL TYPE`
LOB declarations.

## Intended Nodes

- `usage_clause`
- `sql_type_clause`
- `sql_type_name`
- `sql_type_size`
- `blob_type`
- `clob_type`
- `dbclob_type`

## Accepted Forms

```cobol
05 BLOB-IMGN-ANVRSO USAGE IS SQL TYPE IS BLOB(30K).
```

```cobol
05 DOC-TEXT USAGE IS SQL TYPE IS CLOB(3900).
```

```cobol
05 DOC-DBCS USAGE SQL TYPE DBCLOB(12M).
```

## Excluded Forms

- Host-variable semantic validation.
- SQL declarations outside COBOL data-description entries.
- Non-LOB SQL types not observed in the current target samples.
- Full DB2 precompiler validation of maximum lengths or encoding.

## Local Syntax

The rule is scoped as a `usage_clause` variant inside a data-description entry.
It requires `USAGE`, accepts optional `IS`, requires `SQL`, accepts optional
`TYPE IS`, then one LOB type with an optional parenthesized size. Size literals
may be digits alone or digits with a `K`, `M`, or `G` suffix.

## Corpus Coverage

- `test/corpus/data_description.txt`: `sql type lob data description`.

## Audit Notes

Initial target samples include real declarations such as:

```cobol
05 BLOB-IMGN-ANVRSO   USAGE IS SQL TYPE IS BLOB(30K)
```

The rule must be validated against the full COBOL inventory before it can move
from candidate to stable.

## Validation Result

Validated on 2026-08-13 against 74,242 COBOL files with `normal-fixed` layout
normalization.

- Corpus: 186/186 passed.
- Parsed OK: 74,242.
- Hard failures: 0.
- `ERROR` nodes: 4,231 before, 4,151 after.
- `MISSING` nodes: 2 before, 2 after.
- Files improved by `ERROR/MISSING` count: 18.
- Files regressed by `ERROR/MISSING` count: 0.
- Matched `sql_type_clause` nodes: 18 in 13 observed SQL TYPE files.
- Net `error_byte_count` delta: -1,051,267.

Known caution:

- 8 already-dirty files showed larger recovery spans even though their
  `ERROR` and `MISSING` counts did not regress. The details are preserved in
  `audits/sql_type_clause_20260813/match_and_regression_audit.md`.

Artifacts:

- Report: `runs/cobol_sql_type_clause_repair_report.md`.
- Validation DB:
  `runs/candidate_compare_current_sql_type_blob_clause_full_inventory_20260813.sqlite`.
- Audit: `audits/sql_type_clause_20260813/match_and_regression_audit.md`.
