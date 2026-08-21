# Legacy Space Typos

## Rule name

Legacy typo aliases for the COBOL figurative constant `SPACE/SPACES`.

## Purpose

Accept observed Cementera value-clause typos while preserving the canonical `SPACE` node in the AST.

## Included forms

- `SCACES` as `SPACE`.
- `SPCACES` as `SPACE`.

## Excluded forms

- No general fuzzy matching for figurative constants.
- No additional misspellings beyond the observed Cementera source forms.

## Local syntactic shapes supported

```cobol
       01  A PIC X VALUE SCACES.
       01  B PIC X VALUE SPCACES.
```

## Known semantic limits

These aliases tolerate legacy source defects for parsing only. They do not rewrite the original source and do not imply compiler acceptance.

## Corpus examples covered

- `legacy typo value spaces` in `test/corpus/data_description.txt`.

## Audit result summary

Initial target: Cementera residual data-description errors observed in `PPROD242.sqlcbli` and `TESTE.sqlcbli`. Full validation result is recorded in the corresponding `runs/` SQLite report after parser generation.
