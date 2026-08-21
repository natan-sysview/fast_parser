# copy-bib-of-library

## Purpose

Support Cementera-style copybooks named with a `.BIB` suffix in `COPY ... OF ...` statements.

## Basis

Cementera contains:

```cobol
COPY WORKDATA.BIB OF FPREV006.
```

and similar `TELA01.BIB` / `ENTRADA.BIB` forms.

## Included Forms

- `COPY <name>.BIB OF <library>`
- `COPY <name>.bib OF <library>`

## Excluded Forms

- Arbitrary dotted copybook names outside the `.BIB` convention.
- Dotted identifiers in expressions or paragraph names.

## Grammar Shape

Adds named token `copybook_bib_name` as a `copy_statement` book alternative, with higher lexical precedence than generic word tokens.

## Corpus

- `copy_replacing.txt`
  - `copy dotted bib of library`

## Audit Result

Validation `runs/candidate_compare_current_cementera_copy_bib_of_20260821.sqlite`:

- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- ERROR nodes: 156, down from 157
- MISSING nodes: 0, unchanged
- Improved file: `COBHOR10.sqlcbli`
- Regressions: 0
