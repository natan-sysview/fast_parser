# Rule Catalog: Fixed-Format Simple Picture Period

Status: implemented in experimental grammar.

## Goal

Parse fixed-format data descriptions where a simple `PIC` string ends immediately before the statement period in zero-based column 71. Without this rule, the generic `picture_edit` token can consume the period and sequence suffix as part of the picture string.

Examples:

```cobol
012310     05 WS-TASACRENT2E-NUM REDEFINES WS-TASACRENT2E-TEXT PIC 9999.00012310
```

```cobol
060300   05 WS-CUOTA-VAL-PAGO REDEFINES WS-CUOTA-VAL-NUM-PAGO PIC X(06).00060300
```

## Accepted Forms

- Simple alphanumeric pictures such as `PIC X(06).00060300`.
- Simple numeric pictures such as `PIC 9999.00012310`.
- Plain counted numeric pictures such as `PIC 9(3).00027900`.
- Numeric pictures with an implied decimal marker such as `PIC 9(12)V99.` when the period is in fixed-format column 72.
- Only candidates whose picture begins near the right side of the fixed source area, currently zero-based column 60 or later.

## Excluded Forms

- Comma-edited or decimal-edited pictures such as `PIC 999,999,999` and `PIC 9.99`.
- Edited pictures such as `PIC Z,ZZZ,ZZZ,ZZ9.99.00017507`; those are covered by the separate `fixed-format-edited-picture-period` rule.
- `DATE FORMAT` data-description clauses; a normal grammar alternative was tested and rejected because it caused broad regressions.
- Productive `grammars/`; this rule lives only in `experimental-grammars/tree-sitter-cobol`.

## Implementation Shape

The grammar adds hidden external alternatives under `picture_x` and `picture_9`.

The scanner:

- recognizes simple `X` and `9/P/V/Z` picture forms;
- keeps comma-edited masks out of scope;
- only scans candidates starting at column 60 or later;
- lets `_fixed_format_period` terminate the data-description entry.

## Corpus Coverage

- Positive: simple numeric fixed period before sequence digits.
- Positive: simple counted numeric fixed period before sequence digits.
- Positive: simple alphanumeric fixed period before sequence digits.
- Positive: simple numeric fixed period without suffix digits.
- Negative: ordinary `PIC 9.99` remains `picture_edit`.
- Negative: ordinary `PIC X/X` remains `picture_edit`.
- Negative: comma-edited `PIC 999,999,999` remains `picture_edit`.

## Validation Result

Validated on 2026-06-29 over 74,151 non-JCL COBOL inventory files.

- Corpus: 143/143 passed.
- Parsed OK: 74,151.
- Hard failures: 0.
- Parser error-flag files: 10,899 before, 10,666 after.
- Strict `ERROR` files: 10,894 before, 10,661 after.
- `ERROR` nodes: 12,051 before, 11,723 after.
- Files with `MISSING`: 1 before, 1 after.
- `MISSING` nodes: 1 before, 1 after.
- Files became clean by parser flag: 233.
- Files became newly dirty: 0.
- Files with lower `ERROR` count: 246.
- Files with higher `ERROR` count: 1, already dirty (`AE2CLS62`, `DATE FORMAT YYYYXXXX` remains unsupported).

## Artifacts

- Baseline before: `baselines/2026-06-29-before-fixed-format-simple-picture-period-repair`.
- Validation DB: `runs/candidate_compare_current_fixed_format_simple_picture_period_v6_full.sqlite`.
- A/B audit CSVs: `audits/fixed_format_simple_picture_period_v6_repair/`.
- Profile audit CSVs: `audits/profile_validation_current_fixed_format_simple_picture_period_v6/`.
- Repair report: `runs/cobol_fixed_format_simple_picture_period_repair_report.md`.

## Post-SKIP Counted Picture Retry

Retested on 2026-06-30 after the accepted `PROCESS` and `SKIP1/SKIP2/SKIP3`
directive repairs. The earlier exclusion of plain fixed-column `PIC 9(3)` was
removed and covered with a real UR8-style corpus case:

```cobol
000279        10 WS-NRO-PERCAP-NUM REDEFINES WS-NRO-PERCAP-AUX PIC 9(3).00027900
```

Validation DB:

- `runs/candidate_compare_current_fixed_format_counted_picture9_retry_post_skip_full.sqlite`

Baseline DB:

- `runs/candidate_compare_current_skip_directive_full.sqlite`

Result:

- Corpus: 166/166 passed.
- Files: 74,151 -> 74,151
- Parsed OK: 74,151 -> 74,151
- Hard failures: 0 -> 0
- Files with Tree-sitter `has_errors`: 3,196 -> 3,161
- Files with counted `ERROR` nodes: 3,191 -> 3,156
- `ERROR` nodes: 3,847 -> 3,812
- Files with `MISSING`: 1 -> 1
- `MISSING` nodes: 1 -> 1
- `error_byte_count`: 319,260,230 -> 313,055,297
- Changed files: 40
- Became clean: 35
- Became dirty: 0
- Files with lower `ERROR` node count: 35
- Files with higher `ERROR` node count: 3
- Validation throughput: 1,359.1 files/sec

Known existing-dirty regressions:

- `UR8CCMI0`: 1 -> 2 `ERROR` nodes.
- `UR8CINC0`: 1 -> 2 `ERROR` nodes.
- `UR8CINCE`: 1 -> 2 `ERROR` nodes.

Decision: accepted as stable experimental repair. The retry now has a strong
net improvement and no newly dirty files, while the three higher-node UR8 files
remain explicitly documented for follow-up.
