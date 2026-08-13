# Rule Catalog: Fixed-Format Debug Indicator

Status: implemented in experimental scanner.

## Goal

Parse COBOL fixed-format debug lines where column 7 contains `D` or `d` and the executable statement starts in area B.

Enterprise programs commonly contain:

```cobol
000100D    DISPLAY 'DEBUG'
```

The prior scanner skipped sequence columns but did not expose the debug indicator as trivia. The parser then recovered with `ERROR` and often inserted `MISSING "."` at the first statement token after the indicator.

## Accepted Forms

```cobol
000100D    DISPLAY 'DEBUG'.
```

```cobol
      d    DISPLAY 'DEBUG'.
```

## Excluded Forms

- Full source-format conversion.
- Treating debug lines as comments.
- Continuation-line handling beyond the existing scanner behavior.
- Semantic control of COBOL `WITH DEBUGGING MODE`.

The parser keeps the statement body; only the fixed-format indicator character is consumed as scanner trivia.

## Corpus Coverage

- Debug indicator before `DISPLAY`.
- Lowercase debug indicator before `DISPLAY`.

## Validation Plan

- Run focused corpus tests.
- Rebuild FastParse COBOL extension.
- Run compact full-inventory diagnostics.
- Compare against `candidate_compare_current_optional_program_id_period_full.sqlite`.
- Audit residual column-11 `MISSING "."` nodes.

## Validation Result

Validated on 2026-06-25 with compact full-inventory diagnostics over 74,151 non-JCL COBOL files.

- Parser generation: passed.
- Focused corpus: 2/2 `debug_indicator` cases passed.
- Existing full corpus: 96/97 passed; the pre-existing unrelated `comment` corpus failure remains.
- Parsed OK: 74,151.
- Hard failures: 0.
- Files improved: 401.
- Files regressed: 0.
- Files became clean: 399.
- Files became dirty: 0.
- `ERROR` nodes: 58,882 before, 54,669 after.
- `MISSING` nodes: 717 before, 408 after.
- Residual `MISSING "."` at column 11: 313 before, 4 after.
- Compact diagnostics SQLite integrity check: `ok`.

## Artifacts

- Baseline before: `baselines/2026-06-25-before-debug-indicator-repair`.
- Diagnostics DB: `runs/candidate_compare_current_debug_indicator_full.sqlite`.
- Report: `runs/cobol_debug_indicator_repair_report.md`.
- Comparison audit: `audits/debug_indicator_repair/`.
