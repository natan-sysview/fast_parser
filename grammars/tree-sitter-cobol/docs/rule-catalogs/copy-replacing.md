# COPY REPLACING

## Rule Name

`copy_statement`, `replacing_clause`, `copy_replacing_item`

## Purpose

Recognize COBOL `COPY` statements that use the `REPLACING ... BY ...` phrase, including common enterprise forms with `SUPPRESS`.

## Basis

Observed in the local COBOL inventory issue audit after the fixed-format data period repair.

## Included Forms

- `COPY COPYBOOK REPLACING OLD-NAME BY NEW-NAME.`
- `COPY COPYBOOK SUPPRESS REPLACING 'OLD' BY 'NEW'.`
- multiple replacement pairs after one `REPLACING` keyword.
- optional `LEADING` or `TRAILING` before a replacement operand.

## Excluded Forms

- copybook expansion.
- semantic validation of whether replacement operands exist in the copied member.
- pseudo-text delimited by `== ... ==`; this can be added later if confirmed in the inventory.

## Local Syntax Supported

The grammar recognizes the `COPY` statement itself, optional `IN`/`OF` library name, optional `SUPPRESS`, and a `REPLACING` phrase containing one or more replacement pairs.

## Known Limits

This is a syntax recovery and structure rule. It does not resolve copybook paths, expand copybooks, or validate replacement targets.

## Corpus Examples Covered

- single identifier replacement pair.
- `SUPPRESS` plus string-literal replacement pair.
- multiple replacement pairs.
- nearby `INSPECT ... REPLACING` remains a normal procedure statement, not a copy statement.

## Audit Result Summary

Full validation after the repair:

- corpus: 103/103 passed.
- parsed OK: 74,151/74,151.
- hard failures: 0.
- files with `ERROR`: 44,653 -> 44,561.
- `ERROR` nodes: 52,647 -> 51,124.
- files with `MISSING`: 38 -> 17.
- `MISSING` nodes: 38 -> 17.
- newly dirty files: 0.

Source-level audit found 2,036 files with `COPY ... REPLACING` and 88,375 statements. Most CICS/DB2 occurrences are `COPY DEBUGAID SUPPRESS REPLACING ...`; pseudo-text forms remain intentionally excluded and are a separate candidate rule.
