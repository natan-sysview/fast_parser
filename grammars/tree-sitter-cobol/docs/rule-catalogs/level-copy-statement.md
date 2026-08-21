# Level COPY Statement

## Rule Name

`level_copy_statement`

## Purpose

Recognize copy inclusions written with a data level number before `COPY`, such as `03 COPY ...`, inside Data Division entries.

## Included Forms

```cobol
03 COPY DDS-ALL-FORMATS OF RS02LF5.
01 COPY DDS-ALL-FORMATS OF VIAGLANCAL.
```

## Excluded Forms

- Procedure Division `COPY` statements.
- Semantic expansion of the copybook.

## Corpus

- `level copy statement`

## Audit Basis

Observed in Cementera `COPY_REPLACE` residuals such as `PAD004.sqlcbli`, `PPASEF008C.sqlcbli`, and `VIAGEM70.sqlcbli`.
