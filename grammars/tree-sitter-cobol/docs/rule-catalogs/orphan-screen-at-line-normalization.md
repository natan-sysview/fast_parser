# Orphan Screen AT Line Normalization

## Purpose

Ignore fixed-format screen-position lines such as `AT 1102.` when they are orphaned after a completed statement.

## Included Forms

- A physical line containing only `AT nnnn` or `AT nnnn.`
- The previous non-comment source line must already end with a period.

## Excluded Forms

- Continuation-style `AT` lines where the previous source line does not end the statement.
- Inline `AT` clauses that belong to `DISPLAY` or `ACCEPT`.

## Local Syntax

This is parser-input normalization only. The original COBOL bytes stay unchanged. The orphan `AT` line is replaced with spaces in the normalized parser input so it cannot create a standalone syntax error.

## Cementera Audit

- Baseline: `runs/candidate_compare_current_cementera_display_literal_period_before_at_normalization_20260821.sqlite`
- Candidate: `runs/candidate_compare_current_cementera_orphan_screen_at_line_normalization_20260821.sqlite`
- Result: `ERROR` nodes dropped from 36 to 35; `MISSING` nodes stayed at 0.
- Improved file: `PPORTA080.sqlcbli`
- Regressions observed: 0

