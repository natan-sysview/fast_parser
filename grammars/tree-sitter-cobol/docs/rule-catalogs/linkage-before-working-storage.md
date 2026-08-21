# linkage-before-working-storage

## Purpose

Accept legacy programs that place `LINKAGE SECTION` before
`WORKING-STORAGE SECTION` inside `DATA DIVISION`.

## Basis

Some Cementera COBOL programs declare file records, then linkage parameters,
then working-storage variables. The previous grammar only accepted the common
order `WORKING-STORAGE SECTION` before `LINKAGE SECTION`.

## Included Forms

- Optional `FILE SECTION` and `DATABASE SECTION` before the two sections.
- `LINKAGE SECTION` followed by `WORKING-STORAGE SECTION`.
- Existing optional trailing sections after `WORKING-STORAGE SECTION`.

## Excluded Forms

- Arbitrary section reordering.
- Multiple repeated `LINKAGE` or `WORKING-STORAGE` sections.
- Procedure division recovery.

## Corpus

- `data_description.txt`: `linkage before working storage section`.

## Audit

Initial target: Cementera files classified as `DIVISION_SECTION_HEADER` where
`LINKAGE SECTION` appears before `WORKING-STORAGE SECTION`.

Validation result on Cementera:

- Baseline: `291` ERROR nodes, `3` MISSING nodes.
- After rule: `281` ERROR nodes, `3` MISSING nodes.
- Improved files: `10`.
- Regressed files: `0`.
