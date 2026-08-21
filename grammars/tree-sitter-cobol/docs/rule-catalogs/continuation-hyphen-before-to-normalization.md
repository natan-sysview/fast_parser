# Continuation Hyphen Before TO Normalization

## Rule name

`continuation_hyphen_before_to`

## Purpose

Normalize fixed-layout lines where column 7 contains a continuation hyphen immediately before a `TO` phrase, but the previous line already contains a complete literal. In the observed Cementera source, the hyphen acts like visual continuation/sangria rather than a valid COBOL literal continuation and prevents the `MOVE ... TO ...` statement from parsing.

## Included forms

- Normalized physical lines matching:

```text
^\s{6}-\s+TO\b
```

## Excluded forms

- Continuation lines that continue an open literal.
- Continuation lines before anything other than `TO`.
- Normal fixed-format indicator handling outside this exact shape.

## Local syntactic shape

The normalizer replaces only the column-7 hyphen with a space and preserves the original line length and newline.

## Evidence

Baseline:

```text
baselines/2026-08-21-before-cementera-continuation-hyphen-before-to-normalization/cobol_layout_normalization.py
```

Validation DB:

```text
runs/candidate_compare_current_cementera_continuation_hyphen_before_to_normalization_20260821.sqlite
```

Audit DB:

```text
audits/cementera_continuation_hyphen_before_to_normalization_20260821/issue_nodes.sqlite
```

Scope search found two matching lines, both in:

```text
VCP000.cbl
```

## Result

Compared with `current_cementera_orphan_trailing_hyphen_label_normalization_20260821`:

- Files: `4169`
- Parsed OK: `4169`
- Hard failures: `0`
- Files with ERROR: `22 -> 21`
- ERROR nodes: `16 -> 15`
- Files with MISSING: `0 -> 0`
- MISSING nodes: `0 -> 0`
- Improved file: `VCP000.cbl`
- Regressions: none observed

## Known semantic limits

This is not a general continuation-line rewrite. It only repairs the observed `- TO` shape where the surrounding statement is otherwise a normal `MOVE literal TO target` statement.
