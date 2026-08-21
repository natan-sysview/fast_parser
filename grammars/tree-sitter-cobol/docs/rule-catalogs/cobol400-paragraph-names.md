# cobol400-paragraph-names

## Purpose

Allow paragraph and section names that include COBOL/400-style underscores.

## Basis

Cementera contains procedure labels such as:

```cobol
020-READ-FPCA_SFP.
020-READ-FECA_SFP.
```

The grammar already recognized `cobol400_word` for other local constructs, but paragraph and section headers still accepted only numeric labels, plain words, or integers.

## Included Forms

- Paragraph headers with `cobol400_word`.
- Section headers with `cobol400_word`.

## Excluded Forms

- Arbitrary punctuation in paragraph names.
- COPY member names and file names; those have separate rules.

## Grammar Shape

Extends `paragraph_header` and `section_header` name choices with `cobol400_word`.

## Corpus

- `procedure_tolerances.txt`
  - `cobol400 paragraph name with underscore`

## Smoke Result

Local normalized parses became clean for representative Cementera files:

- `PDIARIA006.sqlcbli`
- `PDIARIA010.sqlcbli`
- `PDIARIA200.sqlcbli`

Full Cementera FastParse validation is required after rebuilding the extension.

## Validation Note

Full Cementera validation `runs/candidate_compare_current_cementera_cobol400_paragraph_names_20260821.sqlite` reduced total `ERROR` nodes from 207 to 198. Ten files improved and one file, `PVASI017.sqlcbli`, exposed one additional residual caused by visible `FIXED_SHORT` suffix digits in columns beyond the logical source area. A global `FIXED_SHORT` suffix trim was tested and reverted because it truncated valid long `EXTERNALLY-DESCRIBED-KEY` text in the same profile family.
