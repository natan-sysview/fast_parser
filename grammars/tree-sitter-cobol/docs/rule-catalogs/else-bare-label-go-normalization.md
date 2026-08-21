# ELSE Bare Label GO Normalization

## Purpose

Normalize parser input for a legacy typo where an `ELSE` branch is followed by a bare paragraph label instead of a `GO` statement.

## Included Forms

- Physical line `ELSE`.
- Immediately following physical line shaped like `<label>.`.
- The following line is rewritten in the parser input view as `GO <label>.`.

## Excluded Forms

- Paragraph headers separated from `ELSE` by comments or blank lines.
- Normal paragraph headers.
- Source rewrites; original COBOL bytes are preserved.

## Local Shape

```cobol
ELSE
ROT-LER.
```

becomes:

```cobol
ELSE
GO ROT-LER.
```

## Evidence

- Baseline: `baselines/2026-08-21-before-cementera-else-bare-label-go-normalization/cobol_layout_normalization.py`
- Validation DB: `runs/candidate_compare_current_cementera_else_bare_label_go_normalization_20260821.sqlite`
- Audit DB: `audits/cementera_else_bare_label_go_normalization_20260821/issue_nodes.sqlite`
- Cementera result: `ERROR nodes 27 -> 26`, `MISSING nodes 0 -> 0`.
- Improved file: `CLIPALM05.sqlcbli`.
- Regression guard: nearby clean `STIF010/STIF030/STIF040/STIF050` paragraph headers were excluded by requiring the physical previous line to be exactly `ELSE`.
- Regressions: none found in full Cementera validation.

## Known Limits

This is syntax recovery for a local branch typo. It does not validate the target label semantically.
