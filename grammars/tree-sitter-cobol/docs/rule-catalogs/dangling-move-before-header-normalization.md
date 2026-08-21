# Dangling MOVE Before Header Normalization

## Purpose

Ignore an incomplete standalone `MOVE` line when the next real source line is a paragraph header.

## Included Forms

- A physical source line whose trimmed content is exactly `MOVE`
- Blank/comment lines may appear before the next paragraph header

## Excluded Forms

- Multi-line `MOVE` statements that continue with operands.
- `MOVE` lines followed by a non-header statement.

## Local Syntax

This is parser-input normalization only. The source file is not modified. During paragraph-header closure, a dangling `MOVE` immediately before the header is replaced with spaces instead of being closed as `MOVE.`.

## Cementera Audit

- Baseline: `runs/candidate_compare_current_cementera_orphan_screen_at_line_normalization_20260821.sqlite`
- Candidate: `runs/candidate_compare_current_cementera_dangling_move_before_header_normalization_20260821.sqlite`
- Result: `ERROR` nodes dropped from 35 to 34; `MISSING` nodes stayed at 0.
- Improved file: `PCLISKU05.sqlcbli`
- Regressions observed: 0

