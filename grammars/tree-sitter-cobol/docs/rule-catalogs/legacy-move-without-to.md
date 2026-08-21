# Legacy MOVE Without TO

## Rule Name

`move_without_to_body`

## Purpose

Recognize Cementera legacy shorthand where `MOVE` omits the `TO` keyword:

```cobol
MOVE 0 CDEMPVD OF DCERV710TC.
MOVE ZEROS WQUANT(W) WQUANTE(W) WDIFERA(W) WCX(W).
```

## Included Forms

- `MOVE <value> <destination>`
- `MOVE <value> <destination> <destination> ...`
- Qualified and subscripted destinations.

## Excluded Forms

- Changing normal `MOVE <value> TO <destination>` parsing.
- Treating arbitrary malformed procedure text as a move statement.
- Inferring semantic destination types.

## Local Syntax

`move_statement` first keeps the standard `_move_body`; this tolerance is an
alternative body with lower precedence and appears as `move_without_to_body` so
audits can distinguish it from standard COBOL.

## Corpus

- `test/corpus/legacy_move_without_to.txt`

## Audit Basis

Observed in Cementera files such as `PACAO100.sqlcbli`, `PCERV709.sqlcbli`,
`PCERV711.sqlcbli`, `PCERV809.sqlcbli`, and `PCERV815.sqlcbli`.
