# Legacy Defines Redefines

## Rule name

Legacy `DEFINES` alias for `REDEFINES`.

## Purpose

Accept observed Cementera data-description typo `DEFINES` where COBOL syntax expects `REDEFINES`.

## Included forms

- `03 FILLER DEFINES WCONVDT.`

## Excluded forms

- No general typo matching for data-description clauses.
- No semantic validation that the referenced item exists.

## Local syntactic shapes supported

```cobol
       01 WCONVDT PIC 9(08).
       03 FILLER DEFINES WCONVDT.
          05 WCA2 PIC 9(04).
```

## Known semantic limits

The parse tree uses the existing `redefines_clause` node. The source text remains unchanged.

## Corpus examples covered

- `legacy typo defines as redefines` in `test/corpus/redefines.txt`.

## Audit result summary

Initial target: Cementera residual data-description error observed in `PPALM091.sqlcbli`. Full validation result is recorded in the corresponding `runs/` SQLite report after parser generation.
