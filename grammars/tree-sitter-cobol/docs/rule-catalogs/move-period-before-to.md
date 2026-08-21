# move-period-before-to

## Purpose

Accept a legacy typo where a period appears between the source operand and `TO` in a `MOVE` statement.

## Basis

Cementera contains:

```cobol
MOVE CDPRODUTO.    TO PRODUTO-L.
```

The period after the source operand prematurely terminates the statement in the base grammar.

## Included Forms

- `MOVE <src>. TO <dst>`.

## Excluded Forms

- Arbitrary periods inside other statements.
- Treating a final statement period as optional source punctuation when no `TO` follows.

## Grammar Shape

Adds named node `legacy_period_before_to` as an optional child immediately before `TO` in `_move_body`.

## Corpus

- `legacy_move_without_to.txt`
  - `move with period before to`

## Audit Result

Full Cementera validation `runs/candidate_compare_current_cementera_move_period_before_to_20260821.sqlite` reduced total `ERROR` nodes from 159 to 158 and files with `ERROR` from 185 to 184, with zero `MISSING` nodes before and after. Improved file:

- `PPREVNFL.cblile`

No regressions were found.
