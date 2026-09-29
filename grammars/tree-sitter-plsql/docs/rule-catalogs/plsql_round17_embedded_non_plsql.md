# PLSQL Round 17 - Embedded Non-PLSQL Recovery

## Rule

`legacy_embedded_non_plsql_block` and exact helper line tokens.

## Purpose

Recover one contaminated package body that contains Java/pseudocode lines inside PL/SQL declarations. The rule exposes the contamination explicitly instead of pretending it is valid PL/SQL.

## Included Forms

- Exact `procedure patito` pseudo header with trailing whitespace.
- Exact `class PatitoDaoImpl` pseudo header.
- Exact Java-style assignment/call/printf lines observed in `CBA_AP_AUTOMATICO.pkb`.

## Excluded Forms

- Normal `PROCEDURE patito;` declarations.
- General Java syntax.
- Name-only guesses outside the audited contamination block.

## Evidence

- Corpus: 162/162 after the change.
- Inventory round17: 13,258 files, 0 hard failures, 23 files with ERROR, 234 ERROR nodes, 4 files with MISSING, 6 MISSING nodes.
- Fixed file: `CBA_AP_AUTOMATICO.pkb` moved from 5 ERROR and 5 MISSING to 0/0.
- CR/FNC remained 0 ERROR and 0 MISSING.

## Decision

Stable as a client-specific recovery node. Keep exact unless more contaminated blocks are audited.
