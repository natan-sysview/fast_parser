# COBOL/400 Expression Tolerances

## Rule Name

`unbalanced_compute_expr`

## Purpose

Recognize observed Cementera arithmetic expressions where a `COMPUTE` formula
opens one or more extra parentheses before the next statement boundary.

## Included Form

```cobol
COMPUTE WPERQBRD ROUNDED =
        ((WTOTPROD(09) * 100) / WTOTPROD(07).
```

```cobol
COMPUTE WGRF =
        ((WGRF03 - (QTINTEIRO * WCX(CTRCOL OF DESTO09A))
COMPUTE QTDECIMAL = (WGRF / 100).
```

```cobol
COMPUTE WQTQTD2 =
        (WQTQTD3 - (WQTQTD1 * WCX(Y)
MOVE WQTQTD1 TO QTINTEIRO.
```

## Excluded Forms

- General error recovery for arbitrary malformed expressions.
- Treating the construct as standard COBOL semantics.
- Automatically inserting source text or changing original bytes.

## Local Syntax

The grammar exposes a named `unbalanced_compute_expr` node on the right side of
`COMPUTE` when a parenthesized arithmetic expression reaches a valid arithmetic
expression but does not provide the matching closing parenthesis. Multiple
leading `(` tokens are accepted only inside this `COMPUTE` right-hand-side
tolerance. Cementera also contains the variant where the outer expression starts
with `(` and a nested right-hand arithmetic expression opens another `(` without
closing before the next COBOL statement.

Balanced expressions remain parsed with the existing generic expression shape.

## Corpus

- `compute with omitted closing parenthesis`
- `compute with balanced parenthesis remains generic`
- `compute with double omitted closing parenthesis`
- `compute with internal omitted closing parenthesis`

## Audit Basis

Observed in Cementera files such as:

- `PPROD045.sqlcbli`
- `PESTO009.sqlcbli`
- `PESTO009S.sqlcbli`

This is treated as dialect/source tolerance and must be validated against the
full COBOL inventory before becoming stable.
