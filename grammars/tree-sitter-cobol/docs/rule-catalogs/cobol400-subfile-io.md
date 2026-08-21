# COBOL/400 Subfile I/O Statements

## Rule Name

`cobol400_read_statement`, `cobol400_write_statement`, `cobol400_rewrite_statement`

## Purpose

Recognize COBOL/400 workstation/subfile I/O forms used in Cementera sources without weakening the generic COBOL `READ`, `WRITE`, and `REWRITE` rules.

## Basis

Observed residual parse errors after the `SPACE-FILL` repair include:

- `READ TELA INTO TMFP155NEW-I FORMAT "TMFP155NEW" INDICATORS ARE INDICADORES`
- `READ SUBFILE TELA INTO TMFP155SNE-I FORMAT "TMFP155SNE" INDICATORS ARE INDICADORES`
- `WRITE SUBFILE REG-TELA FROM TMFP155SNE-O FORMAT "TMFP155SNE"`
- `REWRITE SUBFILE REG-TELA FROM TMFP155SNE-I FORMAT "TMFP155SNE"`

The current generic `READ` rule accepted `FORMAT` before `INTO`, while COBOL/400 sources commonly use `INTO` before `FORMAT`.

## Included Forms

- `READ [SUBFILE] file INTO record FORMAT name [INDICATORS ARE name]`
- `READ SUBFILE file NEXT MODIFIED INTO record FORMAT name [INDICATORS ARE name]`
- `WRITE SUBFILE record [FROM value] [FORMAT name] [INDICATORS ARE name]`
- `REWRITE [SUBFILE] record [FROM value] [FORMAT name] [INDICATORS ARE name]`
- `INDIC name` as an accepted abbreviation of `INDICATORS [ARE] name`.
- `READ ... LAST` as part of the same clause family.

## Excluded Forms

- Semantic validation of DDS formats or indicator data groups.
- General free-order statement parsing outside the listed COBOL/400 clauses.
- `AT END`, `INVALID KEY`, and similar imperative branches; those remain handled by surrounding statement recovery/end markers.

## Corpus

- `test/corpus/cobol400_subfile_io.txt`

## Audit Notes

Added after Cementera audit `audits/cementera_accept_space_fill_20260820`, where top residual `OTHER` samples repeatedly showed COBOL/400 workstation I/O with `SUBFILE`, `FORMAT`, and `INDICATORS` clauses. Extended after the `cementera_io_commitment_control_20260820` and `cementera_read_next_modified_20260820` audits to cover `READ SUBFILE ... NEXT MODIFIED ...` and `INDIC name`, which appear in workstation screen/subfile reads and writes.
