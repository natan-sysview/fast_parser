# PLSQL PKB Repair Round 4

## Purpose

Reduce PKB parse errors while preserving the zero-error CREATE TABLE baseline and avoiding Tree-sitter generate conflicts.

## Included Syntax Forms

- `XMLFOREST(expr AS alias)` and `XMLELEMENT(...)`.
- `XMLTYPE(...)`, `XMLTYPE.createxml(...)`, and chained XML methods such as `.extract(...)`.
- `XMLTABLE(path_expression PASSING XMLTYPE(...) COLUMNS ...)`.
- DML qualified column tuples, such as `SET (a.col1, a.col2) = (...)`.
- `UNPIVOT INCLUDE/EXCLUDE NULLS`, including `FOR (column)` and literal aliases.
- `PIVOT(aggregate FOR column IN (... AS alias))`.
- Dotted database links like `table@LINK.DOMAIN`.
- Boolean cursor attributes such as `cursor%NOTFOUND`.
- `CASE` as a legacy column predicate, such as `CASE IN (...)`.
- `LISTAGG(...) WITHIN GROUP (ORDER BY ...)`.
- Aggregate `KEEP(DENSE_RANK FIRST/LAST ORDER BY ...)`.
- `CURSOR(SELECT ...)` expressions.
- PL/SQL compile constants such as `$$PLSQL_UNIT`.
- Deep object/JSON-style attribute references up to six segments.
- Legacy `HAVING ... GROUP BY ...` ordering observed in source.
- Empty parameter calls such as `ROW_NUMBER()`.
- `CAST(...) AT TIME ZONE ...`.
- `new JSON_OBJECT_T` and `new JSON_ARRAY_T`.
- `FORALL ... SAVE EXCEPTIONS`.
- Oracle alternative quoting with `q'[...]'`, `q'(...)'`, `q'{...}'`, and `q'<...>'`.
- Latin-1 identifier characters for names such as `pi_año` and `AÑO`.

## Excluded Forms

- Free-form parsing of embedded Java/C/HTML snippets inside PL/SQL files.
- Mojibake or replacement-character recovery for invalidly decoded source text.
- SQL*Plus standalone slash as a global catch-all, because many DDL/package rules already own optional slash positions.
- Semantic validation of package, object, or type names.

## Corpus Coverage

The corpus now covers 82 total positive tests: 77 PL/SQL smoke tests plus 5 create-table tests. New round-4 tests cover XML functions, pivot/unpivot variants, deep object references, aggregate clauses, `FORALL SAVE EXCEPTIONS`, `q` quotes, and Latin identifiers.

## Inventory Result Summary

Baseline: `runs/plsql_native_validation_full_after_pkb_repair_round3.sqlite`.

Post-change: `runs/plsql_native_validation_full_after_round4_latin_qquote.sqlite`.

| Subtype | Files | ERROR before | ERROR after | MISSING before | MISSING after |
| --- | ---: | ---: | ---: | ---: | ---: |
| CR | 6794 | 0 | 0 | 0 | 0 |
| FNC | 567 | 673 | 602 | 0 | 0 |
| PKB | 1426 | 2257 | 558 | 22 | 34 |
| PKS | 1246 | 2148 | 940 | 1 | 3 |
| PRC | 3225 | 5732 | 4929 | 205 | 270 |

## Remaining Known Error Families

- Cascades after non-PL/SQL snippets embedded in package bodies.
- Local subprogram/declaration blocks appearing after executable statements.
- SQL*Plus slash/show-errors lines inside files that are already in recovery.
- Replacement-character and mojibake fragments from legacy encodings.
- Remaining declaration cascades around `%TYPE`, local cursor/type declarations, and malformed copied code.

## Decision

Stable enough for the experimental baseline only. Do not promote to `grammars` yet: PKB error nodes are much lower and CR remains clean, but MISSING counts increased in PKB/PKS/PRC and require a focused follow-up round.
