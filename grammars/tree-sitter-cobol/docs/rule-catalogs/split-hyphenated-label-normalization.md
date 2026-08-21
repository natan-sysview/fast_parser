# Split Hyphenated Label Normalization

## Rule name

`split_hyphenated_label`

## Purpose

Normalize labels accidentally split as `NNN-NAME.-SUFFIX.`. The extra period before `-SUFFIX` terminates the paragraph name too early and leaves a stray suffix token. The observed intent is a single hyphenated paragraph label.

## Included forms

- A full physical line matching:

```text
\s+[0-9]+-[A-Za-z0-9-]+\.-[A-Za-z0-9-]+\.\s*
```

## Excluded forms

- Normal labels such as `013-ACCEPT-FIM.`
- Multiple statements on one line.
- Non-label expressions containing `.-`

## Local syntactic shape

The normalizer rewrites `NNN-NAME.-SUFFIX.` to `NNN-NAME-SUFFIX.` and pads the end of the line with spaces so the physical line length is preserved.

## Evidence

Baseline:

```text
baselines/2026-08-21-before-cementera-split-hyphenated-label-normalization/cobol_layout_normalization.py
```

Validation DB:

```text
runs/candidate_compare_current_cementera_split_hyphenated_label_normalization_20260821.sqlite
```

Audit DB:

```text
audits/cementera_split_hyphenated_label_normalization_20260821/issue_nodes.sqlite
```

Scope search found one matching line in:

```text
PESTO020NF.sqlcbli
```

## Result

Compared with `current_cementera_continuation_hyphen_before_to_normalization_20260821`:

- Files: `4169`
- Parsed OK: `4169`
- Hard failures: `0`
- Files with ERROR: `21 -> 20`
- ERROR nodes: `15 -> 14`
- Files with MISSING: `0 -> 0`
- MISSING nodes: `0 -> 0`
- Improved file: `PESTO020NF.sqlcbli`
- Regressions: none observed

## Known semantic limits

This rule assumes the observed `.-` inside a paragraph label is a typo. It does not alter general punctuation recovery outside the exact label shape.
