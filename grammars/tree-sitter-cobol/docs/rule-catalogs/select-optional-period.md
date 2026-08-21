# Select Optional Period

## Rule name

Optional period terminator for `select_statement`.

## Purpose

Accept legacy FILE-CONTROL entries where a `SELECT` statement omits the terminating period before another `SELECT` or before `DATA DIVISION`.

## Basis

Cementera contains COBOL/400-style sources with `SELECT ... ORGANIZATION ...` lines that transition to the next file-control entry or to `DATA DIVISION` without a period.

## Included forms

- `SELECT ...` followed by another `SELECT`.
- Final `SELECT ...` followed by `DATA DIVISION`.
- Existing period-terminated `SELECT` statements remain accepted.

## Excluded forms

- No new file-control clauses are added here.
- No source rewriting or insertion of synthetic period nodes.

## Local syntactic shapes supported

```cobol
       SELECT A ASSIGN TO DATABASE-A
           ORGANIZATION IS SEQUENTIAL
       SELECT B ASSIGN TO DATABASE-B
           ORGANIZATION IS INDEXED.

       SELECT A ASSIGN TO DATABASE-A
           ORGANIZATION IS SEQUENTIAL
       DATA DIVISION.
```

## Known semantic limits

This is a tolerance for legacy/incomplete FILE-CONTROL syntax. It does not prove compiler acceptance in every dialect.

## Corpus examples covered

- `select without period before next select` in `test/corpus/select.txt`.
- `select without period before data division` in `test/corpus/select.txt`.

## Audit result summary

Initial target: Cementera residual `FILE_CONTROL_IO` errors observed in `PPREV121.sqlcbli`, `PSUVDL01.sqlcbli`, and `PSUVDL02.sqlcbli`. Full validation result is recorded in the corresponding `runs/` SQLite report after parser generation.
