# Data Division Direct Single FD

## Rule name

Single direct `FD` after `DATA DIVISION`.

## Purpose

Accept legacy COBOL sources that omit the `FILE SECTION.` header and contain exactly one file description before `WORKING-STORAGE SECTION`.

## Included forms

- `DATA DIVISION.` followed directly by one `FD`.
- Existing direct multiple-`FD` forms remain supported.

## Excluded forms

- No new file-description clauses are introduced.
- No semantic inference of missing section headers beyond the local `FD` structure.

## Local syntactic shapes supported

```cobol
       DATA DIVISION.
       FD  DPREV111
           LABEL RECORD ARE STANDARD.
       01  REG-DPREV111.
           COPY DDS-ALL-FORMATS OF DPREV111.
       WORKING-STORAGE SECTION.
```

## Known semantic limits

The parse tree uses the existing `file_section` node even though the source omits the literal section header.

## Corpus examples covered

- `data division direct single fd` in `test/corpus/data_description.txt`.

## Audit result summary

Initial target: Cementera residual `FILE_CONTROL_IO`/data division recovery around `PPREV684.sqlcbl`. Full validation result is recorded in the corresponding `runs/` SQLite report after parser generation.
