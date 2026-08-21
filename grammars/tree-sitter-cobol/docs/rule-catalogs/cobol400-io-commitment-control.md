# COBOL/400 I-O-Control Commitment Control

## Rule Name

`commitment_control_clause`

## Purpose

Recognize direct `COMMITMENT CONTROL` clauses inside the `I-O-CONTROL` paragraph.

## Basis

Cementera sources use forms such as:

- `COMMITMENT CONTROL FOR RESTART PARAMETROS.`
- `COMMITMENT CONTROL FOR XX20 XX14V1 LC50V XX10 XX12 RESTART.`
- Multiple `COMMITMENT CONTROL ... .` clauses in the same `I-O-CONTROL`
  paragraph.

These appeared in residual error and missing-node audits after the FD optional-period repair.

## Included Forms

- `COMMITMENT CONTROL [FOR] <qualified_word>...`
- Multiline resource lists ending at the paragraph period.
- Repeated I-O control clauses separated by one or more periods.

## Excluded Forms

- `APPLY COMMITMENT CONTROL ...`, which remains handled by `apply_clause`.
- Semantic validation of transaction resources.

## Corpus

- `test/corpus/cobol400_io_commitment_control.txt`
  - `io control multiple commitment control clauses with periods`

## Audit Notes

Added after `runs/candidate_compare_current_cementera_fd_optional_period_20260820.sqlite`, where several new missing nodes clustered around direct `I-O-CONTROL` commitment-control clauses.

Extended for Cementera `PPREV541.sqlcbli`, which has two period-terminated
`COMMITMENT CONTROL` clauses before `DATA DIVISION`.

- Baseline: `baselines/before_cementera_io_control_multi_period_clauses_20260821/`
- DB: `runs/candidate_compare_current_cementera_io_control_multi_period_clauses_20260821.sqlite`
- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- Files with ERROR: 45
- ERROR nodes: 40
- Files with MISSING: 0
- MISSING nodes: 0
- Improved files: 1 versus `candidate_compare_current_cementera_display_wvn_bare_attribute_20260821.sqlite`
- Regressions: 0 files.
- Corpus: 292/292 passing.
