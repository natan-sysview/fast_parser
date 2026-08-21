# INPUT-OUTPUT Direct SELECT

## Rule Name

`input_output_section`

## Purpose

Recognize legacy/compact `INPUT-OUTPUT SECTION` bodies where `SELECT` entries appear directly without a `FILE-CONTROL.` paragraph header.

## Included Form

```cobol
INPUT-OUTPUT SECTION.
    SELECT ARQCHEQE ASSIGN TO DATABASE-ARQCHEQE75
           ORGANIZATION IS SEQUENTIAL
           ACCESS MODE IS DYNAMIC
           FILE STATUS IS FS1.
```

## Excluded Forms

- Omitting the period that terminates each `SELECT`.
- Arbitrary file-control clauses outside `INPUT-OUTPUT SECTION`.

## Corpus

- `input output direct select`

## Audit Basis

Observed in Cementera file-control residuals such as `DEVCHQ30.sqlcbli`.
