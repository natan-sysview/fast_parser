# Display Literal Period Before At Normalization

## Purpose

Normalize legacy fixed-format lines where a `DISPLAY` literal has an accidental period before an `AT` screen position.

## Included Forms

- `DISPLAY "text". AT 1120`
- `DISPLAY 'text'. AT 1120`

## Excluded Forms

- Real statement-ending periods.
- Multi-line display bodies.
- Non-display statements.

## Local Syntax

This is a parser-input normalization, not a source rewrite. The original source bytes are preserved. During fixed-layout parser input construction, the intermediate period is removed only when the same physical line matches `DISPLAY <quoted literal>. AT <numeric-position>`.

## Cementera Audit

- Baseline: `runs/candidate_compare_current_cementera_start_split_not_less_than_20260821.sqlite`
- Candidate: `runs/candidate_compare_current_cementera_display_literal_period_before_at_normalization_20260821.sqlite`
- Result: `ERROR` nodes dropped from 37 to 36; `MISSING` nodes stayed at 0.
- Improved file: `PNFEDILA05.sqlcbli`
- Regressions observed: 0

