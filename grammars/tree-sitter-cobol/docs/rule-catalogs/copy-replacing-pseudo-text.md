# COPY REPLACING Pseudo-Text

## Rule Name

`copy_pseudo_text`

## Purpose

Recognize pseudo-text operands inside `COPY ... REPLACING ... BY ...` statements, for example `==:PGMID:== BY =='PROG'==`.

## Basis

The source-level COPY REPLACING audit found 2,807 pseudo-text statements across the COBOL inventory.

## Included Forms

- `==:TOKEN:==`
- `=='literal'==`
- `==WORD==`
- `==TEMP-KEY==`

## Excluded Forms

- multi-line pseudo-text bodies.
- copybook expansion and semantic replacement.
- nested or malformed pseudo-text delimiters.

## Local Syntax Supported

The grammar treats each `==...==` operand as one `copy_pseudo_text` node when it appears as the left or right operand of a copy replacement pair.

## Known Limits

This rule intentionally recognizes same-line pseudo-text only. If multi-line pseudo-text appears in unresolved audit samples, it should be handled as a separate scanner or grammar repair.

## Corpus Examples Covered

- `COPY TRDX00WS REPLACING ==:PGMID:== BY =='SAMA3EDB'==`.
- Multiple same-statement replacement pairs with pseudo-text operands.

## Audit Result Summary

Validation date: 2026-06-26.

- Corpus: 104/104 passed.
- Full COBOL inventory: 74,151 files parsed OK.
- Hard failures: 0.
- Files with `ERROR`: 44,561 -> 44,458.
- `ERROR` nodes: 51,124 -> 51,019.
- Files with `MISSING`: 17 -> 17.
- `MISSING` nodes: 17 -> 17.
- Became clean: 103 files.
- Became dirty: 0 files.

Primary improvement landed in IBM z/OS DB2 and batch profiles. Tandem, Micro Focus, CICS, and copybook slices had no regression in the aggregate metrics for this rule.
