# Flexible Identification Metadata Delimiters

Status: candidate experimental scanner rule.

## Goal

Stop Identification Division metadata comments before aligned division headers
such as:

```text
ENVIRONMENT                     DIVISION.
```

This is needed when optional metadata paragraphs like `AUTHOR` and
`DATE-WRITTEN` omit a final period after their text.

## Included Forms

- `IDENTIFICATION DIVISION`
- `ENVIRONMENT DIVISION`
- `DATA DIVISION`
- `PROCEDURE DIVISION`
- Metadata paragraph starters:
  - `AUTHOR`
  - `INSTALLATION`
  - `DATE-WRITTEN`
  - `DATE-COMPILED`
  - `SECURITY`

The scanner match is case-insensitive and treats runs of spaces or tabs as a
single separator while checking the beginning of a line.

## Excluded Forms

- General free-form keyword normalization outside `comment_entry` scanning.
- Semantic validation of metadata text.
- Rewriting source layout.

## Local Behavior

The custom scanner's `comment_entry` guard now normalizes horizontal whitespace
in candidate delimiter lines before checking whether the line starts with a
known metadata or division keyword. This prevents aligned division headers from
being consumed as metadata text.

## Corpus Examples Covered

- `test/corpus/identification_metadata.txt`:
  `metadata without final period before aligned environment division`

## Validation Result

Pending full inventory validation.
