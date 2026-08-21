# exec-sql-immediate-host-subscript

## Purpose

Prevent SQL parenthesized expressions on the next token or next line from being
misread as COBOL host-variable subscripts.

## Basis

In `EXEC SQL`, a COBOL host variable can have a subscript such as
`:WS-CAMPO(WS-IDX)`. The subscript must be immediately adjacent to the host
variable name. Cementera SQL uses values like `:K4-BOLETO,` followed by a
parenthesized SQL subselect on the next line; the previous grammar could treat
that subselect as the host variable subscript and lose the whole `EXEC SQL`
statement.

## Included Forms

- Immediate host-variable subscripts: `:NAME(IDX)`.
- Host variables followed by comma/whitespace/newline and SQL parentheses.

## Excluded Forms

- Spaced host subscripts like `:NAME (IDX)`.
- Full SQL expression parsing.
- Changes outside `EXEC SQL`.

## Corpus

- `exec_sql.txt`: `exec sql host variable subscript`.
- `exec_sql.txt`: `exec sql host variable before subselect`.

## Audit

Initial target: Cementera `EXEC_SQL_STATEMENT` residuals in `PREC006.sqlcbl`
and `PREC050.sqlcbl`.

Validation result on Cementera:

- Baseline: `280` ERROR nodes, `3` MISSING nodes.
- After rule: `278` ERROR nodes, `3` MISSING nodes.
- Improved files: `2` (`PREC006.sqlcbl`, `PREC050.sqlcbl`).
- Regressed files: `0`.
