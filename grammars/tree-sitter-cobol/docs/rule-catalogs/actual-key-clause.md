# Rule Catalog: Actual Key Clause

Status: deferred; not enabled in the current experimental grammar.

## Rule Name

`actual_key_clause`

## Purpose

Recognize the Burroughs/Unisys-style `ACTUAL KEY` file-control clause inside
`SELECT` statements while preserving ordinary COBOL `RECORD KEY`,
`RELATIVE KEY`, and file-name parsing.

## Basis

Local `OBJECT` project sources contain many `SELECT ... ACTUAL KEY IS ...`
clauses. Earlier smoke A/B notes in `recording-mode-variants.md` deferred this
construct because it could fragment large legacy `OBJECT` programs before
surrounding `SOURCE-COMPUTER` and `OBJECT-COMPUTER` forms were improved.

This candidate was retested after adding narrow support for:

- multi-word `SOURCE-COMPUTER` names,
- multi-word `OBJECT-COMPUTER` names,
- `OBJECT-COMPUTER` `DISK SIZE` clauses,
- `OBJECT-COMPUTER` `MEMORY SIZE ... MODULES` clauses.

## Included Forms

```cobol
       SELECT OPTIONAL F01 ASSIGN TO DISK
              ACCESS MODE IS RANDOM
              ACTUAL KEY IS WS-REC
              FILE STATUS IS WS-FS.
```

Accepted shape:

```text
ACTUAL KEY [IS] <qualified-word>
```

## Excluded Forms

- `ACTUAL` without `KEY`.
- Arbitrary `ACTUAL ...` attributes outside `SELECT` clauses.
- Semantic validation that the referenced key exists in the data division.
- Any file-control clauses other than the local `ACTUAL KEY` form.

## Grammar Shape

`actual_key_clause` is added as one alternative of `_select_clause`:

```text
ACTUAL KEY [IS] qualified_word
```

The rule requires `KEY` to reduce the chance that an identifier named
`ACTUAL` is reclassified as syntax.

## Corpus Coverage

- Positive `ACTUAL KEY IS WS-REC` after `ACCESS MODE IS RANDOM`.
- Regression where `actual` is used as a file name in `SELECT ACTUAL ASSIGN
  TO DISK`.

## Validation Plan

1. Generate parser artifacts.
2. Run full corpus tests.
3. Smoke parse representative `OBJECT` files with `ACTUAL KEY`.
4. Rebuild the FastParse COBOL language extension.
5. Validate the full 74,151-file COBOL inventory.
6. Compare against
   `runs/candidate_compare_current_database_section_fixed_format_edited_picture_full.sqlite`.
7. Audit `actual_key_clause` matches and inspect any regressions.
8. Accept only if total `ERROR`/`MISSING` metrics do not regress.

## Validation Result

Two full-inventory candidate runs were performed on 2026-06-30:

- `runs/candidate_compare_current_burroughs_computer_actual_key_full.sqlite`
- `runs/candidate_compare_current_burroughs_computer_actual_key_at_hex_full.sqlite`

Against baseline
`runs/candidate_compare_current_database_section_fixed_format_edited_picture_full.sqlite`,
the compensated candidate with `ACTUAL KEY` plus `at_hex_literal` had:

- Files: 74,151
- Parsed OK: 74,151
- Hard failures: 0
- Files with `ERROR`: unchanged at 10,401
- `ERROR` nodes: 11,328 -> 11,337
- Files with `MISSING`: unchanged at 1
- `MISSING` nodes: unchanged at 1
- `error_byte_count`: improved by 1,454,411 bytes overall

Decision: defer. The rule recognizes real syntax and reduces error-byte span,
but it still fragments legacy `OBJECT` programs into 9 additional `ERROR`
nodes. It should be retried after the later `OBJECT` data/procedure-section
errors exposed by `ACTUAL KEY` are repaired.

## Post-SKIP Retry Result

Retested on 2026-06-30 after the accepted `PROCESS` and `SKIP1/SKIP2/SKIP3`
directive repairs.

Baseline:

- `runs/candidate_compare_current_skip_directive_full.sqlite`

Candidate:

- `current_actual_key_retry_post_skip`

Corpus:

- Candidate corpus passed: 167/167, including a positive `ACTUAL KEY` case
  and a regression where `actual` remains a file name.

Smoke result:

- Representative `OBJECT` programs moved their first parse error past
  `FILE-CONTROL`, confirming that `ACTUAL KEY` itself was recognized.

Full-inventory result:

- Files: 74,151 -> 74,151
- Parsed OK: 74,151 -> 74,151
- Hard failures: 0 -> 0
- Files with Tree-sitter `has_errors`: 3,196 -> 3,196
- Files with counted `ERROR` nodes: 3,191 -> 3,191
- `ERROR` nodes: 3,847 -> 3,859
- Files with `MISSING`: 1 -> 1
- `MISSING` nodes: 1 -> 1
- `error_byte_count`: 319,260,230 -> 317,835,659
- Net `error_byte_count` delta: -1,424,571
- Changed files: 24, all `OBJECT`/`PROGRAM`
- Files with lower `ERROR` node count: 0
- Files with higher `ERROR` node count: 7
- Became clean: 0
- Became dirty: 0
- Validation throughput: 1,253.3 files/sec

Decision: still deferred. The retry reduced the aggregate error byte span but
increased total `ERROR` nodes by 12, with no files becoming clean. The grammar
change was reverted, generated artifacts were restored to the post-`SKIP`
baseline, and the FastParse COBOL extension was rebuilt without
`actual_key_clause`.

Audit artifacts:

- `audits/actual_key_retry_post_skip/`
- `runs/cobol_actual_key_retry_post_skip_report.md`
