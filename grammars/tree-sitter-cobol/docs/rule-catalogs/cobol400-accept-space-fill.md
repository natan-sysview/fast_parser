# COBOL/400 Accept Space-Fill Attribute

## Rule Name

`SPACE_FILL` in `with_accp_attr`

## Purpose

Recognize COBOL/400 terminal input statements that use `SPACE-FILL` as an `ACCEPT ... WITH` attribute.

## Basis

Cementera sources repeatedly use screen input forms such as:

- `ACCEPT W-NOMECLI AT 1648 WITH AUTO-SKIP SPACE-FILL.`
- `ACCEPT WDESCBAIRRO WITH AUTO-SKIP UPDATE SPACE-FILL AT 1337.`
- `ACCEPT WS-CAMPO WITH REVERSE-VIDEO UPDATE SPACE-FILL.`

The audit after `indicator_clause` found `SPACE-FILL` in 86 files that still had parse issues.

## Included Forms

- `SPACE-FILL` inside `ACCEPT ... WITH` attributes.
- Attribute combinations with existing `AUTO-SKIP`, `UPDATE`, and screen attributes.
- Both clause orders already observed in the source:
  - `ACCEPT name AT pos WITH attrs`
  - `ACCEPT name WITH attrs AT pos`

## Excluded Forms

- `SPACE-FILL` outside `ACCEPT ... WITH`.
- Display attributes for `DISPLAY ... WITH`; this rule only changes `ACCEPT`.
- Semantic validation of terminal behavior.

## Corpus

- `test/corpus/cobol400_accept_space_fill.txt`

## Audit Notes

Added as a narrow COBOL/400 screen-input repair for Cementera. It is expected to reduce repeated `OTHER` error nodes caused by previously unrecognized `SPACE-FILL` tokens and by `WITH ... AT` clause order.
