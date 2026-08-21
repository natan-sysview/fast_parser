# FUNCTION CURRENT-DATE

Status: stable experimental grammar rule.

## Goal

Parse COBOL intrinsic calls using the standard function name
`FUNCTION CURRENT-DATE`, including reference modification:

```text
MOVE FUNCTION CURRENT-DATE(1:8) TO WS-FECHA-SYS.
```

Before this rule, the grammar only tokenized `CURRENT-DATE-FUNC`, so real
`CURRENT-DATE` calls could fall into recovery.

## Included Forms

- `FUNCTION CURRENT-DATE`
- `FUNCTION CURRENT-DATE(1:8)`
- `FUNCTION CURRENT-DATE (1:4)`
- Existing compatibility spelling `CURRENT-DATE-FUNC`

## Excluded Forms

- Semantic validation of intrinsic function return values.
- A full catalog of every COBOL intrinsic function.
- Dialect-specific function aliases not observed in this repair.

## Local Behavior

The existing `function_` node is preserved. This rule only widens the
`CURRENT_DATE_FUNC` terminal to accept the standard spelling `CURRENT-DATE`.

## Corpus Examples Covered

- `test/corpus/function_intrinsic.txt`: `current-date reference modification`
- `test/corpus/function_intrinsic.txt`: `current-date reference modification with spaced call`

## Validation Result

Validated on 2026-08-14 against the COBOL inventory of 74,242 files.

- Corpus: 203/203 passing.
- Parsed OK: 74,242.
- Hard failures: 0.
- Files with `ERROR`: 2,224 before, 1,566 after.
- `ERROR` nodes: 2,597 before, 1,913 after.
- Files with `MISSING`: 0 before, 0 after.
- `MISSING` nodes: 0 before, 0 after.
- Improved files: 658.
- Regressed files: 0.

The inventory scan found 683 COBOL files containing `FUNCTION CURRENT-DATE`,
with 960 occurrences total.

## Artifacts

- Report: `runs/cobol_function_current_date_repair_report.md`
- Validation DB: `runs/candidate_compare_current_function_current_date_20260814.sqlite`
- Audit: `audits/function_current_date_20260814/`
- Baseline: `baselines/2026-08-14-after-function-current-date/`

Decision: stable experimental rule.
