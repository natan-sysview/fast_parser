# PLSQL Round 38 - Keyword Prefix Identifier Guard

## Goal

Protect PL/SQL identifiers and procedure calls whose names begin with reserved
keywords, such as `LOCK_LOTE`, from being split into a keyword token plus a
partial identifier.

## Basis

The full inventory contains real package code with a nested procedure call:

```sql
LOCK_LOTE (p_lote,'I',v_msg_err);
```

During a discarded lexer optimization experiment, `LOCK_LOTE` was tokenized as
`kw_lock` plus the remaining identifier text. The full inventory caught this as
2 `ERROR` nodes in:

`/Users/natanbarronlugo/Desktop/Proyectos/componentes/cobranza/plsqls_externos/pkb/ap_generacion_corrida.pkb`

## Included Forms

- Procedure/function calls whose callee starts with a keyword prefix but is a
  normal identifier.
- Existing keyword-prefix identifier examples such as `SELECT_COUNT`-style
  names and underscore-prefixed declarations.

## Excluded Forms

- No new keyword-prefix recovery rule was added.
- No broad lexer rewrite was accepted.
- No Oracle Forms syntax was reintroduced.

## Grammar Changes

- Removed duplicate keyword definitions in `grammar.js`:
  - `kw_immediate`
  - `kw_keep`
  - `kw_range`
  - `kw_segment`
- Kept the existing `reservedWord` implementation because the attempted
  `RegExp(..., 'i')` rewrite changed tokenization behavior in real code.

## Corpus

Added positive regression:

- `Keyword prefix procedure call stays identifier`

The fixture verifies that `LOCK_LOTE (p_lote,'I',v_msg_err);` parses as a
`ref_call` whose callee is a normal `referenced_element`.

Corpus result:

- Total parses: 160
- Successful parses: 160
- Failed parses: 0

## Inventory Validation

Round 38 full validation:

- Output DB: `runs/plsql_native_validation_round38_keyword_prefix_guard_threads8.sqlite`
- Threads: 8
- Inventory files: 11,021
- Inventory lines: 4,369,801
- Hard failures: 0
- Files with `ERROR`: 0
- Total `ERROR` nodes: 0
- Files with `MISSING`: 0
- Total `MISSING` nodes: 0
- Total AST nodes: 38,926,730
- Encoding normalized: 1,268
- Wall time: 23.85 seconds

Subtype summary:

| Subtype | Files | Lines | ERROR nodes | MISSING nodes |
| --- | ---: | ---: | ---: | ---: |
| CR | 6,794 | 244,515 | 0 | 0 |
| FNC | 467 | 56,991 | 0 | 0 |
| PKB | 1,426 | 3,528,442 | 0 | 0 |
| PKS | 1,246 | 223,844 | 0 | 0 |
| PRC | 1,088 | 316,009 | 0 | 0 |

## Legacy Node Audit

- Output DB: `audits/round38_keyword_prefix_guard/legacy_node_quality_audit.sqlite`
- Inventory files: 11,021
- Audited OK: 11,021
- Audit failures: 0
- Files with visible `legacy_*` nodes: 18
- Total visible `legacy_*` nodes: 19
- Wall time: 24.13 seconds

The visible legacy-node profile stayed unchanged from Round 37.

## Rejected Experiment

The attempted replacement of per-character case-insensitive regexes with
`RegExp(..., 'i')` improved small corpus parse speed but failed full inventory
validation. It split `LOCK_LOTE` as `kw_lock` plus the remaining text. A `\b`
boundary variant was rejected by Tree-sitter's regex processor. The experiment
was reverted.

## Decision

Stable. Round 38 improves regression coverage and source grammar hygiene while
preserving the Round 37 zero-error full-inventory result.
