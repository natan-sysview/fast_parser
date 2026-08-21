# Incomplete Indicator 8 Filler Normalization

## Rule name

`incomplete_indicator8_filler_value_line`

## Purpose

Normalize fixed-layout Cementera lines where column 7 contains indicator `8` and the source area contains an incomplete `03 FILLER PIC X(...) VALUE` header. In the observed source, those physical lines are followed by continuation-like literal lines, but the indicator/value split produces an isolated incomplete data-description entry for the parser input.

## Included forms

- Fixed COBOL source normalized with `normal-fixed`.
- Physical lines matching:

```text
cols 1-6 blank, col 7 = 8, source = 03 FILLER PIC X(<n>) VALUE
```

Equivalent implementation pattern:

```text
\s{6}8\s+03\s+FILLER\s+PIC\s+X\([^)]*\)\s+VALUE\s*
```

## Excluded forms

- Complete `FILLER ... VALUE <literal>` clauses.
- Any non-`FILLER` data item.
- Any level other than `03`.
- Any indicator other than `8`.
- Any free-form or non-normal-fixed layout profile.

## Local syntactic shape

The rule is implemented as a parser-input normalization, not as a grammar.js production. It blanks the full physical line while preserving line length and newline, avoiding byte/point drift for the surrounding file.

## Evidence

Baseline:

```text
baselines/2026-08-21-before-cementera-incomplete-indicator8-filler-normalization/cobol_layout_normalization.py
```

Validation DB:

```text
runs/candidate_compare_current_cementera_incomplete_indicator8_filler_normalization_20260821.sqlite
```

Audit DB:

```text
audits/cementera_incomplete_indicator8_filler_normalization_20260821/issue_nodes.sqlite
```

Scope search found two matching lines, both in:

```text
PPALMSKU77.sqlcbli
```

## Result

Compared with `current_cementera_inline_decorative_after_period_preserve_normalization_20260821`:

- Files: `4169`
- Parsed OK: `4169`
- Hard failures: `0`
- Files with ERROR: `27 -> 26`
- ERROR nodes: `21 -> 20`
- Files with MISSING: `0 -> 0`
- MISSING nodes: `0 -> 0`
- Improved file: `PPALMSKU77.sqlcbli`
- Regressions: none observed

## Known semantic limits

This is intentionally narrow and Cementera-evidence-based. It does not claim that indicator `8` is generally ignorable COBOL; it only neutralizes the observed incomplete `FILLER VALUE` source-shape that otherwise creates an isolated parse error.
