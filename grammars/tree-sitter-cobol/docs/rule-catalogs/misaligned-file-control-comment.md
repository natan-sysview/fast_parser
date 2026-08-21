# misaligned-file-control-comment

## Purpose

Accept single-star descriptive comment lines that appear inside `FILE-CONTROL` but are shifted out of the classic indicator column.

## Basis

Cementera contains:

```cobol
*ARQUIVO DE N.FISCAIS.
SELECT I-MF024 ...
```

after layout normalization, within `FILE-CONTROL`.

## Included Forms

- `*<letter>...` immediately where `FILE-CONTROL` entries are expected.

## Excluded Forms

- Global single-star comments in procedure or data contexts.
- Arithmetic continuation lines beginning with `*`.
- Decorative multi-star procedure comments, covered separately.

## Grammar Shape

Adds `misaligned_file_control_comment` as an alternative inside `_file_control_paragraph`.

## Corpus

- `select.txt`
  - `file control with misaligned single star comment`

## Audit Result

Validation `runs/candidate_compare_current_cementera_misaligned_file_control_comment_20260821.sqlite`:

- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- ERROR nodes: 153, down from 154
- MISSING nodes: 0, unchanged
- Improved file: `PTRANSFERS5.sqlcbli`
- Regressions: 0
