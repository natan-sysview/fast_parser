# cobol400-file-names

## Purpose

Allow COBOL/400-style file names containing underscores in file-oriented statements.

## Basis

The grammar already had `cobol400_word` and used it in `SELECT`, but later file I/O statements still required plain `WORD`. Cementera programs use names such as `FECA_SFP`, `DCALEND_TP`, and `DCALEND_L2` in `OPEN`, `READ`, `DELETE`, and `CLOSE`.

## Included Forms

- `SELECT FECA_SFP ...`
- `OPEN INPUT FECA_SFP DCALEND_TP`
- `READ FECA_SFP`
- `DELETE FECA_SFP`
- `CLOSE FECA_SFP`
- Related file-name lists in `SAME`, `MULTIPLE FILE`, and `USE ... ON`.

## Excluded Forms

- Arbitrary underscores in all COBOL identifiers.
- SQL identifiers and host variables.
- COPY book names; those have separate syntax and replacement semantics.

## Grammar Shape

Adds internal helper `_file_name = cobol400_word | WORD` and uses it only in file-name fields.

## Corpus

- `file.txt`
  - `cobol400 file names in io statements`

## Smoke Result

Local normalized parses for these Cementera files became clean with the generated parser:

- `PCOMIS30.slcblil`
- `PVERVDA05.slcblil`
- `PFILLRATE2.rqlcbli`

Full Cementera FastParse validation is required after rebuilding the extension.
