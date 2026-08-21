# Unmatched Display Before New Code Normalization

## Rule name

`unmatched_display_before_new_code_line`

## Purpose

Normalize truncated `DISPLAY` statements where a physical line starts with `DISPLAY`, contains an unmatched double quote, and the next code line has already started a new COBOL statement or paragraph header. In these cases the source is not a valid continuation; leaving the open literal causes the parser to recover across unrelated statements.

## Included forms

- Lines whose normalized source starts with `DISPLAY`.
- The line has an odd number of double quotes.
- The next nonblank, non-comment code line is either:
  - a known COBOL statement, or
  - an Area A paragraph header for the file layout.

## Excluded forms

- Valid multi-line display continuations.
- Lines with balanced quotes.
- Lines where the next code line is not clearly a new statement/header.
- Single-quote continuations, which are handled by separate rules.

## Local syntactic shape

The normalizer blanks the damaged physical line while preserving line length and newline. This keeps byte/point positions stable for surrounding code.

## Evidence

Baseline:

```text
baselines/2026-08-21-before-cementera-unmatched-display-before-new-code-normalization/cobol_layout_normalization.py
```

Validation DB:

```text
runs/candidate_compare_current_cementera_unmatched_display_before_new_code_normalization_20260821.sqlite
```

Audit DB:

```text
audits/cementera_unmatched_display_before_new_code_normalization_20260821/issue_nodes.sqlite
```

Pre-change scope check found four candidate lines in three files. Full validation accepted two improvements:

```text
DEVCHQ70C.sqlcbli
PTAB120.sqlcbli
```

`VIAGEM42.sqlcbli` was touched by the candidate pattern but retained its pre-existing data-description error and did not regress.

## Result

Compared with `current_cementera_left_shifted_fixed_normalization_20260821`:

- Files: `4169`
- Parsed OK: `4169`
- Hard failures: `0`
- Files with ERROR: `25 -> 23`
- ERROR nodes: `19 -> 17`
- Files with MISSING: `0 -> 0`
- MISSING nodes: `0 -> 0`
- Improved files: `DEVCHQ70C.sqlcbli`, `PTAB120.sqlcbli`
- Regressions: none observed

## Known semantic limits

This rule treats the line as damaged screen text, not as recoverable COBOL continuation. The condition intentionally requires a following statement/header so broad display literals are not blanked just because they contain an unmatched quote.
