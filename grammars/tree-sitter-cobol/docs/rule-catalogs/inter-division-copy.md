# Inter-Division COPY Directives

## Rule Name

`_inter_division_copy_statement`

## Purpose

Accept COBOL `COPY` directives that appear between major divisions, especially
after `PROGRAM-ID` and before `ENVIRONMENT DIVISION`.

Enterprise fixed-format programs often use this form to include shared headers
or environment/data scaffolding. Treating it as ordinary data or procedure
syntax causes recovery to drift into following comments and division headers.

## Included Forms

- `COPY member.` after `IDENTIFICATION DIVISION`.
- `COPY member.` between `ENVIRONMENT DIVISION` and `DATA DIVISION`.
- Existing `COPY ... OF/IN ...`, `SUPPRESS`, and `REPLACING` forms through the
  existing `copy_statement` rule.

## Excluded Forms

- Copybook expansion.
- Semantic validation of where the copied text would be legal after expansion.
- Making `COPY` a global extra that can hide statement or data-entry periods.
- `COPY` in identification metadata paragraphs before `PROGRAM-ID`.
- `COPY` after `DATA DIVISION`, because this can steal legal Data Division
  section-level copy statements such as copy-supplied file layouts.

## Local Syntax Supported

The rule reuses the existing `copy_statement` node and consumes the required
terminating period in the inter-division context. This keeps `COPY` visible in
the parse tree while avoiding a broad preprocessor-style catch-all.

## Corpus

- `test/corpus/inter_division_copy.txt`

Covered cases:

- copy after `PROGRAM-ID`, before `ENVIRONMENT DIVISION`
- copy after `ENVIRONMENT DIVISION`, before `DATA DIVISION`

## Validation Plan

1. Regenerate the parser.
2. Run Tree-sitter corpus tests.
3. Validate targeted full-inventory slices with high `COPY_REPLACE`,
   `COMMENT_OR_DECORATION`, and `DIVISION_SECTION_HEADER` residuals.
4. Run the full non-JCL COBOL inventory if targeted metrics do not regress.

## Expected Impact

The current audit shows many `COPY_REPLACE`, `COMMENT_OR_DECORATION`, and
`DIVISION_SECTION_HEADER` samples around `COPY TRDX00CR.` placed between
`PROGRAM-ID` and `ENVIRONMENT DIVISION`. This repair should reduce those
recovery cascades without changing Data Division or Procedure Division `COPY`
behavior.
