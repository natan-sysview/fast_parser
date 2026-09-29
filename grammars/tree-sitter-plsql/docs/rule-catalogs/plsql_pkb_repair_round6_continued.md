# PLSQL PKB Repair Round 6 Continued

## Purpose

Reduce `ERROR` and `MISSING` nodes found in real PKB inventory files without weakening CREATE TABLE coverage or accepting malformed source as valid PL/SQL.

## Included Syntax Forms

- `TABLE (SELECT ... FROM ...)` collection expressions.
- Direct table functions in `FROM`, for example `FROM Split(value)`.
- Spaced bang inequality: `! =`.
- Parenthesized scalar update targets: `SET (col) = 'value'`.
- SQLPlus `/` followed by legacy `SHOW_ERRORS`.
- `GRANT ... WITH GRANT OPTION`.
- `XMLForest` elements with implicit aliases.
- ANSI `VARCHAR(size BYTE|CHAR)` declarations.
- Local sized integer declarations such as `INTEGER(3)`.
- Outer joins whose final `ON` appears after a chain of right-side `LEFT JOIN`s.

## Excluded Forms

- Oracle `WRAPPED` bodies remain unsupported in the grammar. An attempted opaque payload rule improved wrapped files but caused broad error-recovery regressions, so it was reverted.
- Binary numeric suffixes such as `05D` remain pending. A contextual suffix rule fixed the two Monex PKB occurrences but increased PRC/FNC recovery errors, so it was reverted.
- Clearly malformed or non-PLSQL source is not accepted by grammar rules, including stray Java-like code, missing commas, truncated package bodies, and typo forms like `0.as`.

## Corpus Coverage

`test/corpus/plsql_smoke.txt` now includes positive examples for all included syntax forms above. Full corpus status for this pass: 125/125 passing.

## Inventory Result

Validation DB: `runs/plsql_native_validation_after_round6_required_outer_join.sqlite`

| Subtype | Files | ERROR files | ERROR nodes | MISSING files | MISSING nodes |
| --- | ---: | ---: | ---: | ---: | ---: |
| CR | 6,794 | 0 | 0 | 0 | 0 |
| FNC | 567 | 2 | 10 | 0 | 0 |
| PKB | 1,426 | 11 | 19 | 1 | 5 |
| PKS | 1,246 | 14 | 59 | 2 | 2 |
| PRC | 3,225 | 181 | 740 | 28 | 62 |

Totals: 13,258 files, 0 hard failures, 208 files with `ERROR`, 828 `ERROR` nodes, 31 files with `MISSING`, 69 `MISSING` nodes, 1,268 encoding-normalized files.

## Remaining PKB Buckets

- Unsupported wrapped units: `SQLAB_TRACE_PARSE.pkb`, `SQLAB_TRACE_FILE_IO.pkb`, `PKG_DATOS_CLTS.pkb`.
- Non-PLSQL or malformed source: `CBA_AP_AUTOMATICO.pkb`, `ENV_CBA_PACKAGE.pkb`, `PKGZDHH_CONTROL_BATCH.pkb`, `PKG_FACTURAS.pkb`, `PKG_RAROC.pkb`, `PKG_RC_REPORTES_REGULATORIOS.pkb`.
- Pending valid-looking numeric suffix: `PKGCAPITALES.pkb`, `PKGCAPITALESTMP.pkb` (`05D`), deferred because the attempted rule regressed global recovery.
