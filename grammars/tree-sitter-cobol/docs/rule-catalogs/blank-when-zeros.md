# BLANK WHEN ZEROS

## Rule Name

`blank_clause`

## Purpose

Recognize `BLANK WHEN ZEROS` in data-description entries, especially edited numeric display fields used in Cementera reports.

## Included Forms

- `BLANK ZERO`
- `BLANK WHEN ZERO`
- `BLANK ZEROS`
- `BLANK WHEN ZEROS`

## Excluded Forms

- Semantic validation of whether the picture string is numeric edited.
- Non-COBOL spelling variants outside `ZERO`/`ZEROS`.

## Corpus

- `blank when zeros plural`

## Audit Basis

Observed in Cementera `DATA_DESCRIPTION` residual samples such as `PIC 999.999BB BLANK WHEN ZEROS`.
