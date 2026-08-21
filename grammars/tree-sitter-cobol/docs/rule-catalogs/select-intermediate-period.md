# select-intermediate-period

## Purpose

Accept legacy `SELECT` statements where a period appears before later file-control clauses.

## Basis

Cementera contains file-control entries such as:

```cobol
SELECT DDELIMITE2
       ASSIGN        TO  DATABASE-DDELIMITE2
       ORGANIZATION  IS  SEQUENTIAL
       ACCESS MODE   IS  SEQUENTIAL.
       STATUS        IS FS1.
```

The period after `SEQUENTIAL` prematurely ends the `SELECT` for the previous grammar, leaving `STATUS IS FS1` outside file-control recovery.

## Included Forms

- A period before a subsequent `_select_clause`.
- Existing final period after a `SELECT`.
- Multiple final periods after a `SELECT`, as seen in fixed-format sequence artifacts.

## Excluded Forms

- Nesting a new `SELECT` inside an existing `SELECT`.
- Treating arbitrary environment-division text after a period as a select clause.

## Grammar Shape

Changes `select_statement` from a flat clause repeat to:

```js
repeat($._select_clause),
repeat(seq('.', repeat1($._select_clause))),
repeat('.')
```

This permits clauses after an intermediate period without treating a trailing extra period as the start of another missing clause.

## Corpus

- `select.txt`
  - `select with intermediate period before status`
  - `select with double final period`

## Audit Result

Full Cementera validation `runs/candidate_compare_current_cementera_select_intermediate_period_v2_20260821.sqlite` reduced total `ERROR` nodes from 166 to 159 and files with `ERROR` from 191 to 185, with zero `MISSING` nodes before and after. Improved files:

- `PCKDELI04.sqlcbli`
- `PDELIMITE2.sqlcbli`
- `PINATIVO03.cblile`
- `PINDPIS500.sqlcbli`
- `PPISCONFTC.sqlcbli`
- `PSAULO101.sqlcbli`
- `PTITULOSNF.sqlcbli`

No regressions were found. An earlier optional-period form fixed the `ERROR` nodes but introduced one `MISSING` node in `PSAULO101.sqlcbli`; the final grouped-period form fixed that regression.
