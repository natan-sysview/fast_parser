# Parenthesized Condition Value List

## Rule

`parenthesized_condition_value_list`

## Purpose

Recognize COBOL comparison operands that group multiple accepted values with `OR` or `AND` inside parentheses.

Common enterprise forms:

```cobol
IF FIELD = (SPACES OR LOW-VALUES)
IF RECORRIDO EQUAL (0001 OR 0002 OR 0003)
IF (A = (SPACES OR LOW-VALUES) AND B = ZEROS)
```

## Included Forms

- Parenthesized lists after a comparison operator.
- Items recognized by the existing arithmetic/value expression rule.
- `OR` and `AND` separators inside the parentheses.
- Numeric values, identifiers, literals, figurative constants, and function-like values already supported by `_expr_calc`.

## Excluded Forms

- Full boolean expressions inside the list, such as `(A = B OR C = D)`, which remain handled by `expr`.
- Semantic validation of whether each value is legal for the compared field.
- Rewriting abbreviated COBOL condition semantics beyond local syntax.

## Local Shape

```text
<expr-calc> <comparator> "(" <expr-calc> (OR|AND <expr-calc>)* ")"
```

The rule is intentionally scoped to comparison operands to avoid changing general parenthesized boolean expression behavior.

## Corpus Coverage

- Figurative constants: `SPACES OR LOW-VALUES`.
- Numeric lists: `0001 OR 0002 OR 0003`.
- Nested use inside a parenthesized condition with `AND`.

## Audit Basis

The post-identification metadata missing-node audit found 1,548 missing `)` nodes in 1,517 files. Samples showed many were caused by comparison operands like `= (SPACES OR LOW-VALUES)` and `EQUAL (0001 OR 0002 ...)`.

## Known Limits

The rule does not prove semantic equivalence with compiler condition-name expansion. It only prevents parser recovery from treating valid parenthesized value lists as missing closing parentheses.
