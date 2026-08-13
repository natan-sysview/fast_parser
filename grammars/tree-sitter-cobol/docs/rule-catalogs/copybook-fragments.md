# Copybook Fragments

## Rule Names

- `copybook_definition`
- `copybook_data_definition`
- `copybook_procedure_definition`

## Purpose

Parse standalone COBOL copybooks without requiring `IDENTIFICATION DIVISION`.
The parser can now enter through either full `program_definition` or a copybook
fragment.

## Included Forms

- Data-description copybooks beginning with level numbers such as `01`, `02`,
  `03`, or `77`.
- Copybook data entries containing `EXEC SQL INCLUDE ... END-EXEC`.
- Procedure copybooks containing `ACCEPT`, `MOVE`, `GO`, `EXIT`, and paragraph
  headers.
- `ACCEPT ... WITH AUTO-SKIP`.

## Excluded Forms

- Semantic expansion of copied members.
- Validation that a copybook is used in a compatible host context.
- Full arbitrary procedure parsing at copybook top level beyond the currently
  cataloged statement families.

## Local Syntax Supported

The copybook entry point is selected only when a full program is not present.
Data entries use the same `data_description` and `copy_statement` rules as
program Data Division entries. Procedure fragments expose named
`paragraph_header` nodes for local labels.

## Corpus

- `test/corpus/copybook_fragments.txt`

Covered cases:

- copybook data definition.
- copybook procedure definition.
- copybook `EXEC SQL INCLUDE`.
- copybook `ACCEPT ... WITH AUTO-SKIP`.

## Carlos Validation

Validation DB:
`runs/candidate_compare_current_carlos_copybook_exec_sql_zero_fixed_v4.sqlite`

- COPYBOOK files: 38.
- COPYBOOK files with `ERROR`: 0.
- COPYBOOK `ERROR` nodes: 0.
- COPYBOOK files with `MISSING`: 0.
- COPYBOOK `MISSING` nodes: 0.

Baseline before the Carlos-focused repair had 38 COPYBOOK files with `ERROR`
and 38 COPYBOOK `ERROR` nodes after CP037/layout normalization.

Decision: keep the copybook entry point in the experimental grammar. Do not
promote to `grammars/` without explicit approval.
