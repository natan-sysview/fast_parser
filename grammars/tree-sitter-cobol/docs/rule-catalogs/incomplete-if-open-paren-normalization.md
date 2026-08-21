# Incomplete IF Open Paren Normalization

## Rule name

`incomplete_if_open_paren`

## Purpose

Normalize source lines where an `IF` statement ends immediately after an identifier plus an opening parenthesis, for example `IF WS-VLRTAXIPC(`. This is incomplete source text and causes parser recovery to consume following executable statements.

## Included forms

- A full physical line matching:

```text
\s+IF\s+[A-Za-z0-9-]+\(\s*
```

## Excluded forms

- Complete parenthesized conditions.
- `IF` statements with any operator, operand, or closing parenthesis.
- Non-`IF` expressions.

## Local syntactic shape

The normalizer blanks the incomplete physical line while preserving line length and newline.

## Evidence

Baseline:

```text
baselines/2026-08-21-before-cementera-incomplete-if-open-paren-normalization/cobol_layout_normalization.py
```

Validation DB:

```text
runs/candidate_compare_current_cementera_incomplete_if_open_paren_normalization_20260821.sqlite
```

Audit DB:

```text
audits/cementera_incomplete_if_open_paren_normalization_20260821/issue_nodes.sqlite
```

Scope search found one matching line in:

```text
PARQIPC05.sqlcbli
```

## Result

Compared with `current_cementera_date_placeholder_value_normalization_20260821`:

- Files: `4169`
- Parsed OK: `4169`
- Hard failures: `0`
- Files with ERROR: `19 -> 18`
- ERROR nodes: `13 -> 12`
- Files with MISSING: `0 -> 0`
- MISSING nodes: `0 -> 0`
- Improved file: `PARQIPC05.sqlcbli`
- Regressions: none observed

## Known semantic limits

This treats the exact line as incomplete/damaged source. It does not generalize to valid subscripted conditions or parenthesized expressions.
