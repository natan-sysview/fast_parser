# SELECT Lock Mode WITH LOCK ON RECORD

## Rule Name

`lock_mode_clause`

## Purpose

Recognize `SELECT` file-control clauses that combine `LOCK MODE IS AUTOMATIC` with `WITH LOCK ON RECORD`.

## Included Form

```cobol
SELECT CADHORAS ASSIGN TO "CADHORAS"
       ORGANIZATION IS INDEXED
       LOCK MODE IS AUTOMATIC
       WITH LOCK ON RECORD.
```

## Excluded Forms

- Runtime lock semantics.
- Non-file-control `WITH LOCK` phrases.

## Corpus

- `lock mode with lock on record`

## Audit Basis

Observed in Cementera file-control residuals such as `COBHOR10.sqlcbli` and `PROD050.sqlcbli`.
