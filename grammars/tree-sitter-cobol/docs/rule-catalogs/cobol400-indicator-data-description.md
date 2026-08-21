# COBOL/400 Indicator Data Description Clause

## Rule Name

`indicator_clause`

## Purpose

Recognize COBOL/400 display indicator declarations inside data-description entries, such as `PIC 1 INDIC 03` and `PIC 1 INDICATOR 1`, without treating the indicator keyword as a generic identifier or parse error.

## Basis

Observed Cementera COBOL/400 sources contain repeated indicator fields under `INDICADOR` / `INDICADORES` groups:

- `05 IN03 PIC 1 INDIC 03.`
- `05 IN-FIM-PGM PIC 1 INDIC 03.`
- `05 IN-PROMPT PIC 1 INDIC 04.`
- `05 INDIC-FMT10 PIC 1 INDICATOR 1.`

The form is local to a data-description entry and appears after a `PIC` clause.

## Included Forms

- `INDIC <integer>` as a data-description clause.
- `INDICATOR <integer>` as the long-form data-description clause.
- Numeric indicators with leading zeroes, for example `INDIC 03`.
- Multiple indicator fields in one data group.

## Excluded Forms

- Procedure I/O clauses such as `READ ... INDIC ...` or `WRITE ... INDIC ...`; those belong to read/write statement clauses.
- Full `INDICATORS ARE <name>` clauses already handled by `indicators_clause`.
- Non-numeric indicator operands.

## Local Syntax

```cobol
05 IN03 PIC 1 INDIC 03.
05 IN-FIM-PGM PIC 1 INDIC 05.
05 INDIC-FMT10 PIC 1 INDICATOR 1.
```

## Corpus

- `test/corpus/cobol400_indicator_data_description.txt`

## Audit Notes

Added after Cementera audit `audits/cementera_move_without_to_20260820`, where `PIC 1 INDIC nn` appeared as repeated `DATA_DESCRIPTION` error family samples in PROGRAM and COPYBOOK files. Extended after `cementera_special_names_comma_20260820` to cover the long `INDICATOR n` form observed in `OMP998.cbl` and `OMP999.cbl`.
