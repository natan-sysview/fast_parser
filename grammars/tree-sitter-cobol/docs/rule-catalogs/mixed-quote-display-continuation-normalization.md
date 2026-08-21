# Mixed Quote Display Continuation Normalization

## Rule name

`mixed_quote_display_continuation`

## Purpose

Normalize fixed-layout display continuation lines that open with a single quote but close with a double quote before an `AT nnnn` screen position. The surrounding display text uses double quotes, so the single quote is treated as a source typo.

## Included forms

- A normalized physical line matching:

```text
^\s{6}-\s*'[^']*"\s+AT\s+[0-9]{4}\s*$
```

## Excluded forms

- Valid single-quoted literals.
- Continuation lines without a closing double quote.
- Non-display/screen-position continuations.

## Local syntactic shape

The normalizer replaces only the opening single quote with a double quote, preserving physical line length.

## Evidence

Baseline:

```text
baselines/2026-08-21-before-cementera-mixed-quote-display-continuation-normalization/cobol_layout_normalization.py
```

Validation DB:

```text
runs/candidate_compare_current_cementera_mixed_quote_display_continuation_normalization_20260821.sqlite
```

Audit DB:

```text
audits/cementera_mixed_quote_display_continuation_normalization_20260821/issue_nodes.sqlite
```

Scope search found three matching lines, all in:

```text
PPREV100.sqlcbli
```

## Result

Compared with `current_cementera_incomplete_if_open_paren_normalization_20260821`:

- Files: `4169`
- Parsed OK: `4169`
- Hard failures: `0`
- Files with ERROR: `18 -> 17`
- ERROR nodes: `12 -> 11`
- Files with MISSING: `0 -> 0`
- MISSING nodes: `0 -> 0`
- Improved file: `PPREV100.sqlcbli`
- Regressions: none observed

## Known semantic limits

This only repairs the observed mixed-quote continuation shape. It does not infer or rewrite arbitrary quote mismatches.
