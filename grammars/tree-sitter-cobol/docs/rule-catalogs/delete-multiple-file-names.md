# Delete Multiple File Names

## Purpose

Accept legacy COBOL statements that place more than one file name after `DELETE` in a single statement.

## Included Forms

- `DELETE file-name file-name`
- `DELETE file-name file-name RECORD`
- `DELETE file-name file-name RECORDS`

## Excluded Forms

- Embedded SQL `DELETE FROM ...`, which remains handled by EXEC SQL or existing SQL tolerance rules.
- Semantic validation of whether each file name is open for delete.

## Local Syntax

The `delete_statement` rule now accepts one or more `file_name` fields followed by an optional `RECORD` or `RECORDS` marker.

## Corpus

- `test/corpus/file.txt`: `delete multiple file names`

## Cementera Audit

- Baseline: `runs/candidate_compare_current_cementera_move_period_before_area_a_header_20260821.sqlite`
- Candidate: `runs/candidate_compare_current_cementera_delete_multiple_file_names_20260821.sqlite`
- Result: `ERROR` nodes dropped from 39 to 38; `MISSING` nodes stayed at 0.
- Improved file: `PPORTA004.sqlcbli`
- Regressions observed: 0

