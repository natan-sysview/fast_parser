# Start Split Not Less Than

## Purpose

Accept `START ... KEY IS NOT LESS THAN ...` when `NOT` and `LESS THAN` are separated by a physical line break.

## Included Forms

- `START file-name KEY IS NOT LESS THAN key-name`
- `START file-name KEY IS NOT` followed by `LESS THAN key-name` on the next source line
- The same split-token handling is mirrored for `NOT GREATER THAN`.

## Excluded Forms

- Semantic validation of indexed-file key ordering.
- Non-COBOL typos such as `TRANUM` in place of `THAN`.

## Local Syntax

The relational operator rules now accept `NOT` + `LESS` and `NOT` + `GREATER` as separate tokens in addition to the existing combined-token variants.

## Corpus

- `test/corpus/file.txt`: `start split not less than`

## Cementera Audit

- Baseline: `runs/candidate_compare_current_cementera_delete_multiple_file_names_20260821.sqlite`
- Candidate: `runs/candidate_compare_current_cementera_start_split_not_less_than_20260821.sqlite`
- Result: `ERROR` nodes dropped from 38 to 37; `MISSING` nodes stayed at 0.
- Improved file: `PLOGISTIC1.sqlcbli`
- Regressions observed: 0

