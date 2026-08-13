# SKIP Listing Directives

## Rule Name

`compiler_directive`

## Purpose

Accept fixed-format COBOL listing directives `SKIP1`, `SKIP2`, and `SKIP3` as
compiler directives rather than treating them as COBOL statements, paragraphs,
or metadata text.

## Basis

The residual audit after the `PROCESS` directive repair found multiple IBM z/OS
programs with standalone `SKIP1`, `SKIP2`, or `SKIP3` listing directives between
identification metadata, environment paragraphs, and source sections.

## Local Syntax Supported

The existing `compiler_directive` extra now accepts full-line fixed-format
`SKIP` directives:

- optional six-column sequence area made of spaces or digits,
- optional whitespace,
- `SKIP1`, `SKIP2`, or `SKIP3`, case-insensitively,
- optional whitespace or trailing digits through physical line end.

## Known Limits

- Only `SKIP1`, `SKIP2`, and `SKIP3` are accepted.
- `TITLE`, `SPACE`, and other plain-word listing controls remain excluded until
  separately audited.
- `SKIP1` used inside a COBOL statement or data declaration is not treated as a
  compiler directive because this rule requires the rest of the physical line to
  contain only whitespace or digits.

## Corpus Examples Covered

- `SKIP1`, `SKIP2`, and `SKIP3` before `IDENTIFICATION DIVISION`.
- `SKIP2` with trailing fixed-format line digits.

## Audit Result Summary

Validation date: 2026-06-30.

- Corpus: 165/165 passed.
- Full COBOL inventory: 74,151 files parsed OK.
- Hard failures: 0.
- Files with `ERROR`: 3,272 -> 3,196.
- `ERROR` nodes: 3,911 -> 3,847.
- Files with `MISSING`: 1 -> 1.
- `MISSING` nodes: 1 -> 1.
- Became clean: 76 files.
- Became dirty: 0 files.
- Files with lower `ERROR` node count: 76.
- Files with higher `ERROR` node count: 2.

The two higher-node files are large SQL COBOL programs (`ZM4DH513`,
`ZM4DH514`). In both, accepting `SKIP3` reduces the total error byte span but
exposes later residual `EXEC SQL`/data-region errors as separate nodes. The
aggregate result is accepted because total error files, total error nodes,
error byte span, and throughput improve with no `MISSING` regression.
