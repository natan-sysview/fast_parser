# PLSQL PKB Repair Round 3

## Purpose

Reduce PKB parse errors without regressing CREATE TABLE (`CR`) or the other PL/SQL component classes in the shared inventory.

## Included Syntax Forms

- `PRAGMA` as package declaration and executable statement.
- Scalar/subquery table references with `ORDER BY` and parenthesized compound queries.
- `THE(subquery)` table collection expressions.
- `PIPE ROW(expression)`.
- Boolean predicates over arithmetic expressions, including `BETWEEN`, comparisons, and division.
- `RETURN VARCHAR` without size in PL/SQL function declarations.
- Dynamic `OPEN cursor FOR expression`.
- `SYS.<package>.<type>` datatypes.
- `WHERE CURRENT OF cursor`.
- `IN` expression lists and tuple `IN` predicates.
- `TRIM(...)`, `TRIM(BOTH FROM ...)`, `TRIM(BOTH char FROM ...)`.
- Infix `MOD`.
- `CASE` statements with expression selectors and `CASE` expressions as operands.
- Parenthesized `LIKE` operands.
- Named block endings (`END label`).
- `AT TIME ZONE`.
- Package body initialization blocks.
- `LOCK TABLE ... MODE` without `NOWAIT`/`WAIT`.
- `XMLTABLE(...)` with optional `XMLNAMESPACES`, `PASSING`, and `COLUMNS ... PATH`.
- Function parameters with `DISTINCT`, such as `COUNT(DISTINCT col)`.

## Excluded Forms

- Free-form recovery for malformed or generated fragments.
- Dynamic SQL string parsing beyond normal string literal support.
- SQL*Plus standalone slash as a global catch-all, due previous conflicts with existing optional slash rules.
- Full semantic validation of datatypes, aliases, or schema resolution.

## Corpus Coverage

The smoke corpus now covers 58 positive tests total, including the new forms above. `create_table` remains covered by 5 positive tests, including the parenthesized default regression case.

## Inventory Result Summary

Baseline: `runs/plsql_native_validation_full_after_pkb_repair_round2_final.sqlite`.

Post-change: `runs/plsql_native_validation_full_after_pkb_repair_round3.sqlite`.

| Subtype | Files | ERROR before | ERROR after | MISSING before | MISSING after |
| --- | ---: | ---: | ---: | ---: | ---: |
| CR | 6794 | 0 | 0 | 0 | 0 |
| FNC | 567 | 916 | 673 | 14 | 0 |
| PKB | 1426 | 11152 | 2257 | 443 | 22 |
| PKS | 1246 | 2300 | 2148 | 1 | 1 |
| PRC | 3225 | 6452 | 5732 | 211 | 205 |

## Remaining Known Error Families

- Large cascades in `PV_VALIDA`-style files after unsupported or irregular blocks.
- Encoding/mojibake identifiers and literals shown as replacement characters.
- Generated HTML fragments embedded in string-heavy PL/SQL sections.
- Standalone slash leftovers in already-recovered files.
- Remaining procedure/cursor declaration cascades around complex local type declarations.

## Decision

Stable for experimental grammar baseline. Promote only after another full pass on the remaining top PKB families and after revalidating all subtypes.
