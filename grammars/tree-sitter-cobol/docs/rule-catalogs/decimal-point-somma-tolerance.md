# decimal-point-somma-tolerance

## Purpose

Accept the Cementera legacy typo `DECIMAL-POINT IS SOMMA` in `SPECIAL-NAMES` paragraphs.

## Basis

Three residual Cementera files contain:

```cobol
SPECIAL-NAMES. DECIMAL-POINT IS SOMMA.
```

The intended COBOL phrase is `DECIMAL-POINT IS COMMA`. This tolerance is scoped to the `decimal_point_clause` only.

## Included Forms

- `DECIMAL-POINT IS COMMA`.
- `DECIMAL-POINT IS SOMMA`.

## Excluded Forms

- Treating `SOMMA` as a general synonym outside `decimal_point_clause`.
- Accepting arbitrary misspellings of `COMMA`.
- Changing comma-separated `SPECIAL-NAMES` behavior.

## Grammar Shape

Adds hidden token `_SOMMA` and changes `decimal_point_clause` to accept `choice($._COMMA, $._SOMMA)`.

## Corpus

- `source-object-computer.txt`
  - existing `special names comma separated crt status`
  - new `special names decimal point legacy somma`

## Audit Result

Full Cementera validation `runs/candidate_compare_current_cementera_decimal_point_somma_tolerance_20260821.sqlite` reduced total `ERROR` nodes from 180 to 178 and files with `ERROR` from 205 to 203, with zero `MISSING` nodes before and after. Improved files:

- `PINDPIS03.sqlcbli`
- `PINDPIS06.sqlcbli`

No regressions were found. `PINDPIS500.sqlcbli` still has a residual error after this tolerance, so `SOMMA` was not its only parse issue.
