# Legacy Select Typos

## Rule name

Legacy typo aliases for existing COBOL tokens in file-control and file-description clauses.

## Purpose

Accept a small set of real Cementera source typos without introducing new public typo nodes or broad fuzzy matching.

## Included forms

- `SEQUANTIAL` as `SEQUENTIAL`.
- `DYMAINC` as `DYNAMIC`.
- `OMMITED` as `OMITTED`.

## Excluded forms

- No general edit-distance matching.
- No additional misspellings beyond the observed Cementera forms.
- No semantic correction or source rewriting.

## Local syntactic shapes supported

```cobol
       SELECT F ASSIGN TO DATABASE-F
           ORGANIZATION IS SEQUANTIAL.

       SELECT F ASSIGN TO DISK
           ACCESS MODE IS DYMAINC.

       FD  IMPRESSORA LABEL RECORD IS OMMITED.
```

## Known semantic limits

These spellings are legacy tolerance aliases. The parse tree exposes the canonical token nodes (`SEQUENTIAL`, `DYNAMIC`, `OMITTED`) so downstream tooling does not need to handle typo-specific node types.

## Corpus examples covered

- `legacy typo organization sequantial` in `test/corpus/select.txt`.
- `legacy typo access dymainc` in `test/corpus/select.txt`.
- `legacy typo label record ommited` in `test/corpus/data_description.txt`.

## Audit result summary

Initial target: Cementera residual file-control and file-description errors observed in `PNFEDILA05.sqlcbli` and `TESTE.sqlcbli`. Full validation result is recorded in the corresponding `runs/` SQLite report after parser generation.
