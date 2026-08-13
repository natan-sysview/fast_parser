# Rule Catalog: Fixed-Format Data Period

Status: implemented in experimental grammar.

## Goal

Parse data-description entries whose terminating period is in fixed-format column 72 and is immediately followed by sequence or identification digits.

Examples from the inventory include:

```cobol
008400     05  LT-INI-WS PIC X(41) VALUE '** INICIO WORKING STORAGE **'.00840000
```

```cobol
008800     05  WS-IMPORTE-TOT              PIC S9(13)V9(2) USAGE COMP-3.00880068
```

Without a scoped token for this period, the parser can treat `.00840000` or `.00880068` as a decimal literal and keep the data description open until a later recovery error.

## Accepted Forms

- String `VALUE` ending at column 72 before suffix digits.
- Numeric usage clauses ending at column 72 before suffix digits.

## Excluded Forms

- Global changes to numeric literal precedence.
- Global changes to edited picture tokenization.
- Full fixed-format source conversion.
- Procedure-division periods outside data-description entries.
- Edited picture tokens that begin before column 72 and consume suffix digits, such as `PIC ZZ9.99.00017507`. Those require a separate redesign of `picture_edit`.

## Implementation Shape

The scanner exposes a hidden `_fixed_format_period` token when it sees `.` at zero-based column 71. `_data_division_entry` accepts either a normal `.` or `_fixed_format_period` as its terminating period.

This keeps the repair scoped to data descriptions and avoids changing public trees.

## Corpus Coverage

- `VALUE '...'` followed immediately by suffix digits.
- `USAGE COMP-3` followed immediately by suffix digits.

## Validation Plan

- Generate parser.
- Run focused corpus tests.
- Rebuild FastParse COBOL extension.
- Run compact full-inventory diagnostics.
- Compare against `candidate_compare_current_debug_indicator_full.sqlite`.
- Audit regressions before deciding.

## Validation Result

Validated on 2026-06-25 with compact full-inventory diagnostics over 74,151 non-JCL COBOL files.

- Parser generation: passed.
- Focused corpus: 2/2 `fixed_format_data_period` cases passed.
- Full corpus: 98/99 passed; the pre-existing unrelated `comment` corpus failure remains.
- Parsed OK: 74,151.
- Hard failures: 0.
- Files improved: 4,880.
- Files regressed by node count: 1,298.
- Files became clean: 4,378.
- Files became dirty: 0.
- `ERROR` nodes: 54,669 before, 52,647 after.
- `MISSING` nodes: 408 before, 38 after.
- Error bytes: 3,017,277,932 before, 2,321,066,280 after.
- Compact diagnostics SQLite integrity check: `ok`.

Node-count regressions were reviewed. They occur only in already-dirty files, and the aggregate error-byte coverage still improves by about 696 MB, so the rule is kept.

## Artifacts

- Baseline before: `baselines/2026-06-25-before-fixed-format-data-period-repair`.
- Diagnostics DB: `runs/candidate_compare_current_fixed_format_data_period_full.sqlite`.
- Report: `runs/cobol_fixed_format_data_period_repair_report.md`.
- Comparison audit: `audits/fixed_format_data_period_repair/`.
