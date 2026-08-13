# Rule Catalog: Optional PROGRAM-ID Period

Status: expanded in experimental grammar.

## Goal

Parse enterprise COBOL programs where the `PROGRAM-ID` paragraph omits its terminating period before the next division header or before identification metadata paragraphs.

Some real sources contain:

```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SAMPLE
       ENVIRONMENT DIVISION.
```

The prior grammar inserted `MISSING "."` at `ENVIRONMENT DIVISION` and often recovered with a broad `ERROR` node.

## Accepted Forms

```cobol
       PROGRAM-ID. SAMPLE.
```

```cobol
       PROGRAM-ID. SAMPLE
       ENVIRONMENT DIVISION.
```

```cobol
       PROGRAM-ID. SAMPLE
       DATA DIVISION.
```

```cobol
       PROGRAM-ID. SAMPLE
       AUTHOR.
```

```cobol
       PROGRAM-ID. SAMPLE
       DATE-COMPILED.
```

## Excluded Forms

- Semantic validation of program names.
- Reordering COBOL divisions.
- Treating arbitrary words after `PROGRAM-ID` as metadata unless they match a known identification metadata paragraph header.

The no-period variant is still scoped to local identification-division syntax: standard `PROGRAM-ID. NAME.` remains preferred, and only known identification metadata headers may follow the omitted-period form inside the same division.

## Corpus Coverage

- Standard `PROGRAM-ID. NAME.` remains valid.
- `PROGRAM-ID. NAME` followed by `ENVIRONMENT DIVISION.` parses without a missing period.
- `PROGRAM-ID. NAME` followed by `DATA DIVISION.` parses without a missing period.
- `PROGRAM-ID. NAME` followed by `AUTHOR.` parses without splitting the program.
- `PROGRAM-ID. NAME` followed by `DATE-COMPILED.` parses without splitting the program.

## Validation Plan

- Generate parser.
- Run corpus tests.
- Run compact full-inventory FastParse diagnostics.
- Compare against `candidate_compare_current_symbol_compiler_directives_full.sqlite`.
- Audit the 484 targeted dirty files with `PROGRAM-ID` followed by metadata.
- Audit residual `ERROR` and `MISSING` nodes.

## Validation Result

Validated on 2026-06-25 with compact full-inventory diagnostics over 74,151 non-JCL COBOL files.

- Parser generation: passed.
- Focused corpus: 4/4 `identification_metadata` cases passed.
- Existing full corpus: the new cases passed; the pre-existing unrelated `comment` corpus failure remains.
- Parsed OK: 74,151.
- Hard failures: 0.
- Files improved: 71.
- Files regressed: 0.
- Files became clean: 36.
- Files became dirty: 0.
- `ERROR` nodes: 58,882 before, 58,882 after.
- `MISSING` nodes: 788 before, 717 after.
- Residual `MISSING "."` at column 7: 72 before, 1 after.
- Compact diagnostics SQLite integrity check: `ok`.

## Artifacts

- Baseline before: `baselines/2026-06-25-before-optional-program-id-period-repair`.
- Diagnostics DB: `runs/candidate_compare_current_optional_program_id_period_full.sqlite`.
- Report: `runs/cobol_optional_program_id_period_repair_report.md`.
- Comparison audit: `audits/optional_program_id_period_repair/`.

## 2026-06-26 Expansion: Metadata After Omitted Period

Pre-change audit found 484 dirty files where `PROGRAM-ID. <name>` is followed by identification metadata without a terminating period on the `PROGRAM-ID` paragraph:

- `SQL_COBOL`: 289 files.
- `PROGRAM`: 195 files.

The 2026-06-26 expansion changes only the `identification_division` shape so that the no-period `PROGRAM-ID` variant may be followed by known metadata paragraph headers.

Validation result over 74,151 inventory files:

- `tree-sitter test`: 120/120.
- Parsed OK: 74,151.
- Hard failures: 0.
- Files with parser error flag: 33,100 before, 32,646 after.
- Strict `ERROR` files: 33,092 before, 32,638 after.
- `ERROR` nodes: 35,870 before, 35,520 after.
- `MISSING` nodes: 18 before, 18 after.
- Files became clean: 454.
- Clean files that became dirty: 0.
- Error byte span decreased by 43,930,171 bytes.

Full validation results are recorded in `runs/cobol_program_id_metadata_period_repair_report.md`.
