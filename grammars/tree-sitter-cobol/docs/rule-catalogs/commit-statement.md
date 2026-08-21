# Commit Statement

## Rule name

`commit_statement`.

## Purpose

Recognize standalone COBOL transaction-control `COMMIT` statements used in DB2/SQL COBOL and COBOL/400 code.

## Included forms

- `COMMIT.`
- `COMMIT` before an existing statement boundary such as `END-IF`.

## Excluded forms

- `ROLLBACK`; this rule only adds `COMMIT`.
- `COMMITMENT CONTROL` clauses, which are already handled in I-O control grammar.
- SQL `COMMIT` inside `EXEC SQL ... END-EXEC`, which remains part of `exec_sql_statement`.

## Local syntactic shapes supported

```cobol
           END-EXEC
           COMMIT
       END-IF.
```

## Known semantic limits

This rule recognizes syntax only. It does not validate transaction scope or database mode.

## Corpus examples covered

- `commit statement` in `test/corpus/transaction_control.txt`.
- `commit without period before end-if` in `test/corpus/transaction_control.txt`.

## Audit result summary

Validation artifact: `runs/candidate_compare_current_cementera_commit_statement_20260821.sqlite`.

- Corpus: `259/259` passed.
- Cementera files: `4,169`.
- Parsed OK: `4,169`.
- Hard failures: `0`.
- ERROR nodes: `413 -> 410`.
- MISSING nodes: `3 -> 3`.
- File-level comparison: `3` improved, `0` regressed.

Decision: keep. The rule removes standalone transaction-control `COMMIT` errors without changing SQL-body parsing.
