# Rule Catalog: Value Literal Case Variants

Status: implemented in the experimental grammar after v2 validation.

## Goal

Make COBOL value literals behave more consistently with the rest of the
grammar's case-insensitive keyword handling.

The current grammar accepts uppercase-prefixed string literals such as
`X'74'`, `H'F1'`, and `N'Z'`, but rejects lowercase variants observed in the
inventory. It also enumerates only all-lower, all-upper, and title-case
figurative constants, rejecting mixed forms such as `SPACEs` and `ZEROes`.

## Intended Nodes

- `x_string`
- `h_string`
- `n_string`
- `SPACE`
- `ZEROS`
- `QUOTE`

## Accepted Forms

```cobol
01 WS-XHEX PIC X VALUE x'74'.
01 WS-HHEX PIC X VALUE h'F1'.
01 WS-NCHAR PIC N VALUE n'Z'.
```

```cobol
01 WS-SPACE PIC X VALUE SPACEs.
01 WS-ZERO  PIC 9 VALUE ZEROes.
01 WS-QUOTE PIC X VALUE QUOTEs.
```

The rule also keeps existing uppercase forms accepted:

```cobol
01 WS-XHEX PIC X VALUE X'74'.
01 WS-SPACE PIC X VALUE SPACES.
```

## Excluded Forms

- Invalid or unterminated string literals.
- Multi-line prefixed string literals.
- New literal prefix families not already represented by the grammar.
- Arbitrary mixed-case figurative constants beyond the observed/corpus-covered
  forms.
- Semantic validation of whether a literal matches its `PICTURE`.

## Pre-Change Inventory Audit

Baseline: `runs/candidate_compare_current_dfhvalue_expression_full.sqlite`.

- Lowercase `VALUE x'...'`: 5 SQL_COBOL files, all dirty.
- Lowercase `x'...'` anywhere: 61 files, 45 dirty, 89 matches.
- Lowercase `h'...'` anywhere: 58 files, 40 dirty, 75 matches.
- Lowercase `n'...'` anywhere: 58 files, 36 dirty, 69 matches.
- `VALUE SPACEs`: 2 SQL_COBOL files, all dirty.
- `VALUE ZEROes`: 2 SQL_COBOL files, all dirty.

## Corpus Examples

- `test/corpus/value_literal_case_variants.txt`: lowercase `x`, `h`, and `n`
  prefixed value literals.
- `test/corpus/value_literal_case_variants.txt`: mixed-case `SPACEs`,
  `ZEROes`, and `QUOTEs`.

## Validation Plan

- Generate parser artifacts.
- Run full corpus.
- Build the FastParse COBOL extension.
- Validate the full COBOL inventory.
- Compare against the DFHVALUE baseline.
- Audit targeted files and update this catalog with final metrics.

## Validation Result

Validated on 2026-06-26 against the COBOL inventory.

- `tree-sitter generate`: passed.
- `tree-sitter test`: 126/126 passed.
- FastParse native build: passed.
- Inventory files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- Strict ERROR files: 32,638 before, 32,634 after.
- ERROR nodes: 35,516 before, 35,508 after.
- MISSING nodes: 18 before, 18 after.
- Files became clean: 4.
- Clean files became dirty: 0.
- Regressed files: 0.
- Validation throughput: 998.0 files/sec.

## Targeted Result

- Target patterns: 61 files with lowercase `x'...'`, 58 with lowercase
  `h'...'`, 58 with lowercase `n'...'`, 2 with `VALUE SPACEs`, and 2 with
  `VALUE ZEROes`.
- Improved files by diagnostics: 9.
- Strict clean files: `QC1CPF6`, `QC1CPFM`, `QC6CPFI`, and `BG4CIND1`.

## V1 Discard

An initial implementation used broad case-insensitive regexes for figurative
constants. That version cleaned more files but increased `ERROR` and `MISSING`
nodes. It was discarded and replaced with the current v2 approach: regexes for
prefixed string families, enumerated observed variants for figurative
constants.

## Artifacts

- Report: `runs/cobol_value_literal_case_variants_v2_repair_report.md`.
- Full validation DB:
  `runs/candidate_compare_current_value_literal_case_variants_v2_full.sqlite`.
- Profile report:
  `runs/cobol_value_literal_case_variants_v2_profile_validation_summary_report.md`.
- Repair audit: `audits/value_literal_case_variants_v2_repair/`.
- Profile audit:
  `audits/profile_validation_current_value_literal_case_variants_v2/`.
