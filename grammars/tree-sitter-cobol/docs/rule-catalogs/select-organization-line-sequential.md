# SELECT ORGANIZATION LINE SEQUENTIAL

## Rule Name

`organization_clause`

## Purpose

Recognize `ORGANIZATION LINE SEQUENTIAL` in file-control `SELECT` entries.

## Included Form

```cobol
SELECT WORKHORA ASSIGN TO "WORKHORA"
       ORGANIZATION LINE SEQUENTIAL.
```

## Excluded Forms

- Runtime behavior of line sequential files.
- Non-SELECT uses of `LINE`.

## Corpus

- `organization line sequential`

## Audit Basis

Observed in Cementera `COBHOR10.sqlcbli` after exposing the preceding `WITH LOCK ON RECORD` clause.
