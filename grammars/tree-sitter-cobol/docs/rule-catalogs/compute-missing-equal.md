# compute-missing-equal

## Purpose

Accept legacy `COMPUTE` statements where the equality operator is omitted before the arithmetic expression.

## Basis

Cementera contains forms such as:

```cobol
COMPUTE WVAL ROUNDED ( OPRVALTOT * QTDPED )
```

Standard COBOL writes this as `COMPUTE WVAL ROUNDED = (...)`. The missing equal causes recovery at the parenthesized expression.

## Included Forms

- `COMPUTE <target> [ROUNDED] <expr>`.
- Parenthesized arithmetic expressions as the right side.

## Excluded Forms

- Removing the equality requirement from unrelated statements.
- Semantic validation of arithmetic target types.

## Grammar Shape

Changes `compute_statement` to a choice of the standard form and named `legacy_compute_missing_equal`.

## Corpus

- `cobol400_expression_tolerances.txt`
  - `compute rounded missing equal before parenthesized expression`
  - existing balanced and unbalanced compute cases remain covered.

## Audit Result

Full Cementera validation `runs/candidate_compare_current_cementera_compute_missing_equal_20260821.sqlite` reduced total `ERROR` nodes from 172 to 167 and files with `ERROR` from 197 to 192, with zero `MISSING` nodes before and after. Improved files:

- `PACORD115.sqlcbli`
- `PESTO048.sqlcbl`
- `PMERCADOR.sqlcbli`
- `PMERCADOR1.sqlcbli`
- `PREFR410.sqlcbli`

No regressions were found.
