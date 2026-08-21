# if-header-before-procedure-paragraph

## Purpose

Tolerate an abandoned `IF` header before the next procedure paragraph.

## Basis

Cementera contains procedural fragments such as:

```cobol
CONT-ABRE-CLIMOV.
    IF FS1 NOT = "00"
*
ROTINA-MENU.
```

The previous parse treated the `IF` as the start of a large malformed block and swallowed subsequent paragraphs into `ERROR`.

## Included Forms

- `IF <condition>` immediately before the next procedure paragraph transition.
- Conditions using `NOT =`, with `_NOT_EQUAL` given lexical precedence over separate `NOT` plus `=`.

## Excluded Forms

- Full validation of whether the abandoned `IF` is semantically intentional.
- Rewriting the `IF` into a complete statement.
- Paragraph transitions outside `PROCEDURE DIVISION`.

## Grammar Shape

Adds `if_header` as an accepted final item in `_procedure_division_statements_before_header`. `_NOT_EQUAL` is tokenized with precedence so `NOT =` is parsed as `ne`.

## Corpus

- `procedure_tolerances.txt`
  - `if header without body before paragraph`
- `abbreviated_comparison_continuation.txt`
  - `not equal symbol in if header`

## Audit Result

Cementera validation:

- DB: `runs/candidate_compare_current_cementera_if_header_before_paragraph_20260821.sqlite`
- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- Files with ERROR: 175
- ERROR nodes: 146
- Files with MISSING: 0
- MISSING nodes: 0
- Improved files: 4
  - `PDPMEMB.sqlcbli`: 1 -> 0
  - `PFUNPRO01.sqlcbli`: 1 -> 0
  - `PPALM062.sqlcbli`: 1 -> 0
  - `PRV10015.sqlcbli`: 2 -> 1
- Regressions: 0 files.
