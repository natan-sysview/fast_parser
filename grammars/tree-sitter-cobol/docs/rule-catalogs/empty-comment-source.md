# Empty And Comment-Only Source

## Rule name

`start`

## Purpose

Allow COBOL inventory members with no parseable program or copybook body to parse
as an empty `start` node when they contain only empty input, comments, or compiler
directives already accepted as extras.

## Basis

The full-inventory validation dated 2026-08-13 classified 917 dirty `PROGRAM`
members as `EMPTY_FILE`. These are input/inventory members, not COBOL syntax
constructs that require an `ERROR` node.

## Included forms

- Empty file.
- Fixed-format decorative comment-only member.
- Compiler-directive-only member where the directive already matches
  `compiler_directive`.

## Excluded forms

- Non-empty COBOL text that is not recognized by the grammar.
- Partial programs with malformed required divisions.
- Copybooks with invalid data or procedure entries.

## Local syntactic shapes supported

The top-level `start` rule accepts zero or more `program_definition` nodes, or a
`copybook_definition`. Comments and compiler directives remain extras.

## Known semantic limits

An empty parse does not mean the member is semantically meaningful COBOL; it only
means the source has no grammar-bearing content after extras are removed.

## Corpus examples covered

- `empty source`
- `fixed-format decorative comments only`
- `compiler directive only`

## Audit result summary

- Corpus: 188/188.
- Direct empty-file smoke: `tree-sitter parse /private/tmp/empty-cobol.cbl`
  returned `(start [0, 0] - [0, 0])`.
- Full inventory: 74,242 files.
- Files with `ERROR`: 3,517 -> 2,600.
- `ERROR` nodes: 4,151 -> 3,234.
- Files with `MISSING`: 2 -> 2.
- `MISSING` nodes: 2 -> 2.
- Improved files: 917.
- Regressed files: 0.
