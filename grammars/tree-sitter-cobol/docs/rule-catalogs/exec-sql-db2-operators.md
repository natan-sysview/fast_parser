# Rule Catalog: EXEC SQL DB2 Operators

Status: implemented in experimental grammar.

## Goal

Recognize common DB2 SQL operators inside embedded COBOL `EXEC SQL ... END-EXEC` bodies without introducing a full SQL grammar.

Residual audit examples include:

```sql
E.ESTADO_ENC ^= :DCLEP1-ENCPAQUETERIA.ESTADO-ENC
```

```sql
CVE_CATALOGO||CODIGO||SUBCODIGO >= :LLAVE-CATD
```

## Included Forms

- DB2 not-equal operator `^=`.
- DB2/string concatenation operator `||`.
- Existing SQL comparison and arithmetic operators already supported by `_sql_operator`.

## Excluded Forms

- Full DB2 SQL expression grammar.
- Semantic validation of SQL identifiers, table aliases, or host variables.
- SQL dialect-specific optimizer directives.
- Changes outside embedded `EXEC SQL` bodies.

## Implementation Shape

Add `^=` and `||` to the hidden `_sql_operator` token. This keeps the repair scoped to `sql_body`; COBOL procedure expressions and CICS bodies do not use this token.

## Corpus Coverage

- `WHERE E.ESTADO_ENC ^= :WS-ESTADO`.
- `WHERE CVE_CATALOGO||CODIGO||SUBCODIGO >= :LLAVE-CATD`.

## Validation Plan

- Generate parser.
- Run `tree-sitter test`.
- Rebuild FastParse COBOL extension.
- Run full inventory validation.
- Compare against `runs/candidate_compare_current_fixed_format_numeric_value_period_value_item_scoped_full.sqlite`.
- Audit new dirty files and SQL_COBOL deltas before deciding.

## Validation Result

Validated on 2026-06-26 against the full COBOL inventory.

- Corpus: 111/111 passed.
- Inventory files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- Strict files with `ERROR`: 34,185 before, 33,798 after.
- `ERROR` nodes: 37,545 before, 36,623 after.
- Files with `MISSING`: 18 before, 18 after.
- `MISSING` nodes: 18 before, 18 after.
- Files became clean by strict `ERROR`: 387.
- Files became newly dirty by strict `ERROR`: 0.
- Files with lower `ERROR` count: 706.
- Files with higher `ERROR` count: 6.
- Net error-byte reduction: 64,042,561 bytes.

Known residual:

- Six already-dirty SQL_COBOL files increased in `ERROR` node count after recovery changed. The largest node-count regressions are `MF4C6410` and `SM4CL210`; no file became newly dirty.

## Artifacts

- Baseline before: `baselines/2026-06-26-before-exec-sql-db2-operators-repair`.
- Validation DB: `runs/candidate_compare_current_exec_sql_db2_operators_full.sqlite`.
- Profile report: `runs/cobol_exec_sql_db2_operators_profile_validation_summary_report.md`.
- Audit CSVs: `audits/exec_sql_db2_operators_repair/`.

Decision: kept as stable experimental repair with documented existing-dirty recovery tradeoffs.
