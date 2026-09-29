# PLSQL round33 trailing dot number alias

## Rule name

`trailing_dot_number_alias`

## Purpose

Represent Oracle-style select-list text such as `0.as num_titulos_t4` as a normal trailing-dot numeric alias instead of a recovery node.

Oracle numeric literals can use a decimal point. In the local corpus the source text has no whitespace between the trailing dot and `AS`; treating it locally in select lists avoids broad lexer changes that could damage range syntax such as `1..10`.

## Included forms

- `number . AS alias` without whitespace between `.` and `AS`, as in `0.as num_titulos_t4`.
- Quoted or backslash-quoted aliases through the same alias choices already used by select-list elements.
- Stable fields:
  - `value`: the numeric token before the trailing dot.
  - `alias`: the select-list alias.

## Excluded forms

- General trailing-dot numeric literals across every expression position.
- Range syntax or numeric member access ambiguity.
- Malformed select list columns missing `AS` or an alias.

## Corpus examples covered

- `Trailing dot numeric alias`

## Audit summary

The rule matches the existing Monex package-body case in `PKG_RC_REPORTES_REGULATORIOS.pkb`. It reduces visible `legacy_*` nodes by one while preserving 0 `ERROR` and 0 `MISSING` across the full inventory.
