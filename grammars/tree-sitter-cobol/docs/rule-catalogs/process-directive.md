# PROCESS Compiler Directives

## Rule Name

`compiler_directive`

## Purpose

Accept IBM fixed-format `PROCESS` compiler directive lines as COBOL extras so
they do not block parsing before `IDENTIFICATION DIVISION` or between ordinary
COBOL constructs.

## Basis

The current residual audit after the `LINKAGE SECTION` copy-only repair found a
cluster of z/OS batch programs that start with one or more fixed-format
`PROCESS` lines, for example:

- `000100 PROCESS RENT TRUNC(OPT) ZWB NOSSR`
- `000200 PROCESS NOCMPR2 DATA(31) NUMPROC(PFD) OPT APOST`
- `PROCESS DATA(31),RENT,RES,NUMPROC(PFD),OPT,NOSSR,TRUNC(OPT)`

These lines are compiler directives, not COBOL division headers or statements.

## Local Syntax Supported

The existing `compiler_directive` extra now accepts these local shapes:

- Optional fixed-format sequence area followed by whitespace and `PROCESS`.
- Leading whitespace followed by `PROCESS`.
- `PROCESS` at the beginning of the line followed by directive options.
- Case-insensitive spelling of `PROCESS`.
- Directive options are consumed through the end of the physical line.

## Known Limits

- The parser does not validate individual IBM compiler options such as `RENT`,
  `TRUNC(OPT)`, `DATA(31)`, or `NUMPROC(PFD)`.
- The directive is represented as a generic `compiler_directive` node, matching
  the existing `$$SET`, `]COMP`, `]SAVE`, and `EJECT` handling.
- This rule intentionally does not make top-level `compiler_directive` a normal
  `start` child; it remains an extra so ordinary COBOL grammar structure stays
  unchanged.

## Corpus Examples Covered

- Two fixed-format `PROCESS` directives before `IDENTIFICATION DIVISION`.
- Existing symbol directive examples before `IDENTIFICATION DIVISION`.

## Audit Result Summary

Validation date: 2026-06-30.

- Corpus: 164/164 passed.
- Full COBOL inventory: 74,151 files parsed OK.
- Hard failures: 0.
- Files with `ERROR`: 3,455 -> 3,272.
- `ERROR` nodes: 4,090 -> 3,911.
- Files with `MISSING`: 1 -> 1.
- `MISSING` nodes: 1 -> 1.
- Became clean: 183 files.
- Became dirty: 0 files.
- Error-node regressions: 4 files, each +1 `ERROR` node.

The four node-count regressions were inspected. In each case, recognizing
`PROCESS` lets the parser reach a later unsupported `I-O-CONTROL` /
`APPLY WRITE-ONLY` construct. The aggregate error byte span still decreases in
all four files, so the repair is accepted as a net grammar improvement and the
remaining `I-O-CONTROL` family is tracked as the next repair target.
