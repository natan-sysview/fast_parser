# Write Before Paragraph

## Rule name

`write_statement` as the final statement before a following paragraph header.

## Purpose

Accept legacy COBOL/400 print/report code where `WRITE ... FORMAT ...` omits the terminating period before the next paragraph label.

## Included forms

- Existing `write_statement` forms followed by a paragraph header.
- `WRITE REGIMP FORMAT IS "RCAB01"` followed by `020-...`.

## Excluded forms

- No new `WRITE` clauses are introduced here.
- No general "any statement before paragraph" tolerance is added.

## Local syntactic shapes supported

```cobol
       020-IMPRIME-DADOS-01.
           WRITE REGIMP FORMAT IS "RCAB01"
       020-IMPRIME-DADOS-02.
           MOVE PEDNRO TO RPEDNRO.
```

## Known semantic limits

This is a legacy parse tolerance for paragraph-boundary recovery. It does not insert a synthetic period node.

## Corpus examples covered

- `write without period before paragraph` in `test/corpus/procedure_tolerances.txt`.

## Audit result summary

Initial target: Cementera residual repeated `WRITE REGIMP FORMAT IS ...` errors in `PNOTAPED03.sqlcbli`. Full validation result is recorded in the corresponding `runs/` SQLite report after parser generation.
