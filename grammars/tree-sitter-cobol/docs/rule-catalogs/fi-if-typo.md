# fi-if-typo

## Purpose

Accept `FI` as a legacy typo for `IF` only in an `if_header`.

## Basis

Cementera contains:

```cobol
FI FS1 NOT = "00"
```

The surrounding code shows this is intended to be an `IF` statement.

## Included Forms

- `FI <condition>` where an `if_header` is syntactically expected.

## Excluded Forms

- Treating `FI` as a global synonym for `IF`.
- Reclassifying data names or paragraph names named `FI`.

## Grammar Shape

Adds named token `legacy_fi_if_keyword` as an alternative to `_IF` in `if_header`.
The token requires trailing whitespace so identifiers such as `FIM` are not split as `FI`.

## Corpus

- `abbreviated_comparison_continuation.txt`
  - `legacy fi typo in if header`

## Audit Result

Validation `runs/candidate_compare_current_cementera_fi_if_typo_20260821.sqlite`:

- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- ERROR nodes: 157, down from 158
- MISSING nodes: 0, unchanged
- Improved file: `PINDPIS70.sblcbli`
- Regressions: 0
