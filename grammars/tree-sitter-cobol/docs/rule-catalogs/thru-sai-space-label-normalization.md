# THRU SAI Space Label Normalization

## Purpose

Normalize parser input for singleton range labels written as `THRU <label> SAI.` where the intended COBOL paragraph name shape is `<label>-SAI`.

## Included Forms

- `THRU <label> SAI.`
- `THROUGH <label> SAI.`
- The `SAI` token must be immediately followed by the statement period.

## Excluded Forms

- Non-range uses of `SAI`.
- `THRU` ranges whose target label is already hyphenated.
- Source rewrites; original COBOL bytes are preserved.

## Local Shape

The parser input view replaces the space before `SAI` with a hyphen, preserving line length:

```cobol
PERFORM TESTA-PERNOITE THRU PERNOITE SAI.
```

becomes:

```cobol
PERFORM TESTA-PERNOITE THRU PERNOITE-SAI.
```

## Evidence

- Baseline: `baselines/2026-08-21-before-cementera-thru-sai-space-normalization/cobol_layout_normalization.py`
- Validation DB: `runs/candidate_compare_current_cementera_thru_sai_space_normalization_20260821.sqlite`
- Audit DB: `audits/cementera_thru_sai_space_normalization_20260821/issue_nodes.sqlite`
- Cementera result: `ERROR nodes 32 -> 31`, `MISSING nodes 0 -> 0`.
- Improved file: `VIAGEM08.sqlcbli`.
- Regressions: none found in full Cementera validation.

## Known Limits

This is syntax recovery for a local legacy typo. It does not prove the target paragraph exists semantically.
