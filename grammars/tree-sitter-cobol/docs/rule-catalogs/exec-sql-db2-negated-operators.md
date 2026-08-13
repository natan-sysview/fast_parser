# Rule Catalog: EXEC SQL DB2 Negated Operators

Status: implemented in experimental grammar.

## Goal

Recognize remaining DB2 negated comparison operators inside embedded COBOL `EXEC SQL ... END-EXEC` bodies.

Residual audit examples include:

```sql
FE_FIN_VIGEN ^< :FECHA-FIN-ALTA
```

```sql
FE_INIC_VIGEN ^> :FECHA-FIN-ALTA
```

```sql
IMPVALOR ¬= 0
```

## Included Forms

- `^<`
- `^>`
- `¬=`

## Excluded Forms

- Full DB2 SQL expression grammar.
- COBOL procedure expressions outside `EXEC SQL`.
- Semantic validation of SQL comparisons.
- Non-DB2/client-specific operators not observed in the residual audit.

## Implementation Shape

Add the three operators to hidden `_sql_operator`. The non-ASCII `¬=` operator is represented in `grammar.js` using the ASCII JavaScript escape `\u00ac=`.

## Corpus Coverage

- `WHERE FE_FIN_VIGEN ^< :FECHA-FIN-ALTA`.
- `WHERE FE_INIC_VIGEN ^> :FECHA-FIN-ALTA`.
- `WHERE IMPVALOR ¬= 0`.

## Validation Plan

- Generate parser.
- Run `tree-sitter test`.
- Rebuild FastParse COBOL extension.
- Run full inventory validation.
- Compare against `runs/candidate_compare_current_exec_sql_db2_operators_full.sqlite`.
- Audit new dirty files and SQL_COBOL deltas before deciding.

## Validation Result

Validated on 2026-06-26 against the full COBOL inventory.

- Corpus: 114/114 passed.
- Inventory files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- Strict files with `ERROR`: 33,798 before, 33,777 after.
- `ERROR` nodes: 36,623 before, 36,571 after.
- Files with `MISSING`: 18 before, 18 after.
- `MISSING` nodes: 18 before, 18 after.
- Files became clean by strict `ERROR`: 21.
- Files became newly dirty by strict `ERROR`: 0.
- Files with lower `ERROR` count: 38.
- Files with higher `ERROR` count: 0.
- Net error-byte reduction: 2,270,848 bytes.

Impact is limited to `SQL_COBOL`; `COPYBOOK` and `PROGRAM` counts were unchanged.

## Artifacts

- Baseline before: `baselines/2026-06-26-before-exec-sql-db2-negated-operators-repair`.
- Validation DB: `runs/candidate_compare_current_exec_sql_db2_negated_operators_full.sqlite`.
- Profile report: `runs/cobol_exec_sql_db2_negated_operators_profile_validation_summary_report.md`.
- Audit CSVs: `audits/exec_sql_db2_negated_operators_repair/`.

Decision: kept as stable experimental repair. No file became newly dirty and no existing-dirty file regressed.
