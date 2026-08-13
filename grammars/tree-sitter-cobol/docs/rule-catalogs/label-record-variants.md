# Label Record Variants

## Rule Name

`label_records_clause`

## Purpose

Recognize the common `LABEL RECORD(S) IS/ARE STANDARD` file-description variants found in IBM fixed-format COBOL inventories.

## Basis

After the `FD` copy-record repair, residual `FILE_CONTROL_IO` samples still showed unsupported label clauses:

- `LABEL RECORD ARE STANDARD`
- `LABEL RECORDS IS STANDARD`

A source scan across the 74,151 non-JCL COBOL inventory files found:

- `LABEL RECORD ARE STANDARD`: 24,677 matches in 9,035 files.
- `LABEL RECORDS IS STANDARD`: 1,206 matches in 584 files.

The grammar already handled `LABEL RECORD IS STANDARD` and `LABEL RECORDS ARE STANDARD`.

## Included Forms

- `LABEL RECORD IS STANDARD`
- `LABEL RECORD ARE STANDARD`
- `LABEL RECORDS IS STANDARD`
- `LABEL RECORDS ARE STANDARD`
- The same singular/plural forms with `OMITTED`.

## Excluded Forms

- Non-standard label values beyond `STANDARD` and `OMITTED`.
- Semantic validation of label handling.
- Other `FD` clauses such as Tandem `VALUE PROTECTION`.

## Local Syntax Supported

The `_records` helper accepts optional `IS` or `ARE` after both `RECORD` and `RECORDS`, preserving the existing public tree shape under `label_records_clause`.

## Known Limits

This rule does not decide whether singular/plural agreement is semantically preferred. It only accepts observed compiler-tolerated variants.

## Audit Result Summary

Validation date: 2026-06-26.

- Corpus: 106/106 passed.
- Full COBOL inventory: 74,151 files parsed OK.
- Hard failures: 0.
- Files with `ERROR`: 42,276 -> 35,233.
- `ERROR` nodes: 46,672 -> 40,288.
- Files with `MISSING`: 17 -> 18.
- `MISSING` nodes: 17 -> 18.
- Files with any Tree-sitter issue: 42,283 -> 35,241.
- Became clean by `ERROR` nodes: 7,043 files.
- Became dirty by `ERROR` nodes: 0 files.

The single new `MISSING` occurs in `UB4CEST3`, which changed from 1 `ERROR` and 0 `MISSING` to 0 `ERROR` and 1 `MISSING` at EOF after `COPY QRWCDB20.`. This is tracked as a residual EOF recovery issue, not as a hard parse failure.
