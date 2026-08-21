# Program-ID Bare Attributes

## Rule name

`_program_id_paragraph`

## Purpose

Accept enterprise COBOL programs that write `PROGRAM-ID. NAME INITIAL.` or
`PROGRAM-ID. NAME COMMON.` without the optional `IS` keyword.

## Included forms

```cobol
       PROGRAM-ID. TRDCUINI INITIAL.
```

```cobol
       PROGRAM-ID. TRDCUINI COMMON.
```

The existing forms with `IS INITIAL` and `IS COMMON` remain accepted.

## Excluded forms

- Other identification paragraph attributes not already represented in the
  grammar.
- Semantic validation of whether a compiler permits a given attribute
  combination.

## Local syntactic shapes supported

`is_initial` and `is_common` accept an optional `IS` followed by `INITIAL` or
`COMMON`.

## Known semantic limits

This rule only recognizes local syntax in the `PROGRAM-ID` paragraph. It does
not validate nested program semantics.

## Corpus examples covered

- `program id bare initial attribute`
- `program id bare common attribute`

## Audit result summary

- Corpus: 190/190.
- Full inventory: 74,242 files.
- Files with `ERROR`: 2,600 -> 2,597.
- `ERROR` nodes: 3,234 -> 3,231.
- Files with `MISSING`: 2 -> 2.
- `MISSING` nodes: 2 -> 2.
- Improved files: 3.
- Regressed files: 0.
