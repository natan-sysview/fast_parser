# PLSQL round16 exact DML missing comma repair

Date: 2026-06-26

## Rule name

`legacy_dml_missing_comma_column`

## Purpose

Recover one Monex package body where an `INSERT` column list has a line comment after `id_pago` and the next column `SIT_ENVIO_API` appears without the comma separator.

## Included forms

Only this exact token is accepted as a missing-comma recovery inside `_dml_column_list`:

```sql
INSERT INTO t (
  id_pago--solicitud
  SIT_ENVIO_API
)
VALUES (x);
```

## Excluded forms

- General adjacent DML columns without commas.
- Missing commas before any token other than exact `SIT_ENVIO_API`.
- Missing commas in SELECT lists, parameter lists, value lists, or other grammar contexts.

## Local syntactic shapes supported

The rule is available only inside `dml_column_list_repeat` and emits the named token node `legacy_dml_missing_comma_column`.

## Known semantic limits

This is source-damage recovery, not valid Oracle PL/SQL. It is intentionally exact because a broad missing-comma rule would hide real syntax errors.

## Corpus examples covered

- `Legacy exact DML missing comma column`
- `Adjacent DML column without legacy token stays erroneous`

## Audit result summary

Inventory text audit found `SIT_ENVIO_API` once:

`/Users/natanbarronlugo/Desktop/Proyectos/componentes/monex/pkb/PKGZDHH_CONTROL_BATCH.pkb:350`

Round16 improved that file from 1 `ERROR` node to 0, with no observed regressions.

Decision: stable for the experimental enterprise grammar profile.
