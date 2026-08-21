# move-trailing-sequence-digit

## Purpose

Tolerate a physical-line sequence digit after a complete `MOVE ... TO ...` statement.

## Basis

Cementera contains lines such as:

```cobol
MOVE NMBAIRRO OF R-DVASI01L18 TO RCDBAIR3                   2
```

where the final `2` appears in the fixed-format suffix area.

## Included Forms

- `MOVE <src> TO <dst> <digits>` where the digits are followed by end-of-line.

## Excluded Forms

- Digits followed by paragraph text such as `090-FIM`.
- Semantic numeric operands in the destination list.
- `MOVE` without `TO`, which is covered separately.

## Grammar Shape

Adds named token `legacy_move_trailing_sequence_digit` as an optional final child of `_move_body`.

## Corpus

- `legacy_move_without_to.txt`
  - `move with trailing sequence digit`

## Audit Result

Pending full Cementera validation after parser generation and FastParse extension rebuild.
