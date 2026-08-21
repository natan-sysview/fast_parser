# COBOL/400 Select Assignment Names

## Rule Name

`database_assignment_name`, `control_area_clause`

## Purpose

Recognize COBOL/400 `SELECT` clauses that assign files to database/workstation resources whose names include underscores, and workstation `CONTROL-AREA` clauses.

## Basis

Cementera `FILE-CONTROL` residual errors repeatedly showed forms such as:

- `ASSIGN TO DATABASE-FECA_SFP`
- `ASSIGN TO WORKSTATION-OMF998-SI`
- `CONTROL-AREA IS WS-CTR`

The generic COBOL word token intentionally does not accept `_`, so this repair is scoped to assignment names only.

## Included Forms

- Assignment targets matching `[A-Za-z][A-Za-z0-9_-]*` inside `ASSIGN`.
- `CONTROL-AREA [IS] <qualified_word>` inside `SELECT`.

## Excluded Forms

- General COBOL identifiers with underscores outside assignment targets.
- Semantic validation of database or workstation resources.
- Non-`SELECT` uses of `CONTROL-AREA`.

## Corpus

- `test/corpus/cobol400_database_assignment.txt`

## Audit Notes

Added after Cementera validation `runs/candidate_compare_current_cementera_cobol400_subfile_io_20260820.sqlite`, where `FILE_CONTROL_IO` remained a top residual family and `ASSIGN TO DATABASE-*` appeared across hundreds of files.
