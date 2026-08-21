# decorative-comment-statement

## Purpose

Accept legacy decorative marker lines such as `******AQUI` when they appear in procedure statement positions.

## Basis

Cementera contains decorative markers after COBOL statements and as standalone procedure lines.

## Included Forms

- `**...` as a procedure statement.
- `END-IF. ******AQUI` where the marker follows a completed statement period.

## Excluded Forms

- Single-star fixed-format comment lines.
- Arithmetic continuation operators such as `* 100`.
- Data division comment recovery.

## Grammar Shape

Adds named `decorative_comment_statement` to `_statement` with a token requiring at least two leading asterisks.

## Corpus

- `comment.txt`
  - `decorative comment after period`

## Audit Result

Validation `runs/candidate_compare_current_cementera_decorative_comment_statement_20260821.sqlite`:

- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- ERROR nodes: 154, down from 156
- MISSING nodes: 0, unchanged
- Improved files: `PATULINHA.sqlcbli`, `PPOSIR103.sqlcbli`
- Regressions: 0
