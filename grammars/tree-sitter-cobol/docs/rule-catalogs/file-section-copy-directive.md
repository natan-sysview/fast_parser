# File Section COPY Directives

## Rule Name

`_file_section_copy_statement`

## Purpose

Accept `COPY ... .` entries directly inside `FILE SECTION`, before or between
`FD`/`SD` file descriptions.

Several enterprise programs keep file section metadata in copybooks, for
example:

```cobol
       FILE SECTION.
       COPY MKWCMASC.
       FD  ACLTMRG
```

Without a local `FILE SECTION` copy entry, the parser can either report the
copy itself as an error or recover too far and mark later `FD`/data entries.

## Included Forms

- `COPY member.` directly after `FILE SECTION.`
- Multiple direct `COPY member.` entries before the first `FD`/`SD`.
- Existing `COPY ... OF/IN ...`, `SUPPRESS`, and `REPLACING` forms through the
  existing `copy_statement` rule.

## Excluded Forms

- Copybook expansion.
- Semantic validation that the copied member contains file descriptions.
- Making `COPY` a global extra.
- Changing `FD ... COPY ...` record-layout handling, which is covered by
  `file-description-copy-records.md`.

## Local Syntax Supported

The rule reuses `copy_statement` and consumes the required period only in the
`FILE SECTION` context. `COPY` remains visible in the parse tree.

## Corpus

- `test/corpus/file_section_copy.txt`

Covered cases:

- one `COPY` before an `FD`
- multiple `COPY` entries before an `FD`

## Validation Plan

1. Regenerate parser.
2. Run corpus.
3. Validate full COBOL inventory with layout normalization.
4. Compare `FILE_CONTROL_IO` and Data Division residuals and confirm no clean
   file regression.
