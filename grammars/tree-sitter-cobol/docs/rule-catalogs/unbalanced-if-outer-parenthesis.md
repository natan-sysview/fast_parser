# unbalanced-if-outer-parenthesis

## Purpose

Accept COBOL dialect code where an `IF` condition opens an outer parenthesis and omits only that outer closing parenthesis before the first imperative statement.

## Basis

Cementera SQL_COBOL files contain production forms such as:

```cobol
IF (A NOT = B OR
   (C NOT = 2 AND 5)
   GO TARGET.
```

and:

```cobol
IF ((A NOT EQUAL "N" AND "F" AND "R")
   GO TARGET
END-IF.
```

## Included Forms

- `IF (` followed by a valid COBOL boolean expression where the outer `)` is omitted.
- `ELSE IF (` with the same condition shape.
- Inner balanced parentheses remain parsed by the normal `expr` rule.

## Excluded Forms

- General unbalanced arithmetic expressions outside `IF`/`ELSE IF`.
- Missing parentheses inside SQL, CICS, data descriptions, or COMPUTE expressions.
- Arbitrary malformed conditions that cannot be reduced to a valid `expr` after the single omitted outer close.

## Grammar Shape

The public node is `unbalanced_parenthesized_condition` under the `condition` field of `if_header` and `else_if_header`.

## Corpus

- `condition_parenthesized_value_list.txt`
  - `unbalanced outer if parenthesis before goto`

## Audit Result

Local `tree-sitter parse` on the two Cementera files with current `MISSING` nodes showed that this rule removes the three `MISSING ")"` nodes:

- `PGRID001.sqlcbli`: two missing closes removed; one broader `ERROR` remains.
- `PPREV665P.sqlcbli`: one missing close removed; no remaining `ERROR` or `MISSING` in the local parse.

Full Cementera FastParse validation is required after rebuilding the extension.
