# Explicit User Class Condition

## Rule Name

`is_not_user_class`

## Purpose

Recognize the narrow COBOL class-condition form:

```cobol
IF M57ENTII IS NOT W-DATOS-NUMERI
```

This addresses the residual `MISSING ">="` in `CN1CK570` without widening the global comparison grammar.

## Included Forms

- `identifier IS NOT hyphenated-class-name`

The condition tail must match `IS NOT <hyphenated-name>`, for example `IS NOT W-DATOS-NUMERI`.

The tail is tokenized as a complete local phrase to avoid introducing a generic hyphenated-name token that can compete with normal COBOL `WORD` tokens.

## Excluded Forms

- `IS NOT EQUAL [TO]`
- `IS NOT GREATER [THAN]`
- `IS NOT LESS [THAN]`
- `IS NOT NUMERIC`
- `IS NOT ALPHABETIC`
- SQL predicates such as `IS NOT NULL`
- Non-hyphenated user class names

## Basis

Inventory scan after the restored stable baseline found 25,404 raw `IS NOT <word>` matches, dominated by existing comparison/class predicates:

- `NUMERIC`: 17,601
- `EQUAL`: 6,847
- `NULL`: 606
- `GREATER`: 45
- `LESS`: 24

Restricting to `IS NOT <hyphenated-word>` found only two raw matches:

- one source comment with `PRO-`
- one real COBOL condition in `CN1CK570`: `W-DATOS-NUMERI`

## Corpus Examples

- `explicit is not user class`

Nearby forms such as `IS NOT NUMERIC`, `IS NOT EQUAL`, and `IS NOT GREATER` are guarded by full-inventory regression checks rather than minimal corpus examples because they are not all cleanly represented by the current base grammar.

## Prior Rejected Shapes

The broader `is_not_class` change with optional `IS` was rejected because full inventory validation regressed from 2,338 files with `ERROR` and 2 `MISSING` nodes to 9,315 files with `ERROR` and 300 `MISSING` nodes.

An initial `is_not_user_class` version with a separate `user_class_name` token was also rejected. It reduced `MISSING` nodes from 2 to 1, but full inventory validation regressed to 11,800 files with `ERROR` and 24,296 `ERROR` nodes because the hyphenated-name token competed with ordinary COBOL words.

## Validation Plan

- Generate parser.
- Run `explicit_user_class_condition.txt`.
- Run full corpus.
- Smoke parse `CN1CK570`.
- Validate full inventory and require no increase in `ERROR` nodes or files.

## Validation Result

Candidate: `current_explicit_user_class_condition_v2_20260814`

- Corpus: 195/195
- Inventory files: 74,242
- Parsed OK: 74,242
- Hard failures: 0
- Files with `ERROR`: 2,338 -> 2,337
- `ERROR` nodes: 2,971 -> 2,971
- Files with `MISSING`: 2 -> 1
- `MISSING` nodes: 2 -> 1
- Changed files: 1
- Regressed files: 0

Residual `MISSING`: `CG2C0340`, caused by an unmatched standalone `END-EXEC` in source.

Decision: stable.
