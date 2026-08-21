# Orphan Trailing Hyphen Label Normalization

## Rule name

`orphan_trailing_hyphen_numeric_label`

## Purpose

Normalize isolated numeric labels that contain only digits followed by a trailing hyphen, for example `031-`. This source shape is not a valid paragraph name in the current grammar and, in the observed Cementera case, behaves like an incomplete/orphan label before normal executable statements.

## Included forms

- A full physical line matching:

```text
\s+[0-9]+-\s*
```

## Excluded forms

- Normal numeric paragraph names such as `031-SAI.`
- Numeric labels containing a second component, such as `100-READ`
- Labels with a period and valid name text
- Procedure references such as `GO TO 031-SAI`

## Local syntactic shape

The normalizer blanks the whole physical line while preserving line length and newline.

## Evidence

Baseline:

```text
baselines/2026-08-21-before-cementera-orphan-trailing-hyphen-label-normalization/cobol_layout_normalization.py
```

Validation DB:

```text
runs/candidate_compare_current_cementera_orphan_trailing_hyphen_label_normalization_20260821.sqlite
```

Audit DB:

```text
audits/cementera_orphan_trailing_hyphen_label_normalization_20260821/issue_nodes.sqlite
```

Scope search found one matching line in:

```text
PESTO080.sqlcbli
```

## Result

Compared with `current_cementera_unmatched_display_before_new_code_normalization_20260821`:

- Files: `4169`
- Parsed OK: `4169`
- Hard failures: `0`
- Files with ERROR: `23 -> 22`
- ERROR nodes: `17 -> 16`
- Files with MISSING: `0 -> 0`
- MISSING nodes: `0 -> 0`
- Improved file: `PESTO080.sqlcbli`
- Regressions: none observed

## Known semantic limits

This does not add general support for trailing-hyphen paragraph names. It treats the observed line as incomplete source text and leaves valid numeric paragraph names untouched.
