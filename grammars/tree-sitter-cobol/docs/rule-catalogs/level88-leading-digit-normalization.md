# Level 88 Leading Digit Normalization

## Purpose

Normalize parser input for a legacy fixed-layout artifact where a stray digit appears immediately before a level `88` condition-name entry.

## Included Forms

- Lines matching seven leading spaces, one digit, then a level `88` entry.
- The digit is blanked, preserving line length.

## Excluded Forms

- Valid numeric level numbers.
- Digits outside the specific leading artifact position.
- Source rewrites; original COBOL bytes are preserved.

## Local Shape

```cobol
       1         88 IN26-ON VALUE B"1".
```

becomes:

```cobol
                 88 IN26-ON VALUE B"1".
```

## Evidence

- Baseline: `baselines/2026-08-21-before-cementera-level88-leading-digit-normalization/cobol_layout_normalization.py`
- Validation DB: `runs/candidate_compare_current_cementera_level88_leading_digit_normalization_20260821.sqlite`
- Audit DB: `audits/cementera_level88_leading_digit_normalization_20260821/issue_nodes.sqlite`
- Cementera result: `ERROR nodes 31 -> 30`, `MISSING nodes 0 -> 0`.
- Improved file: `PPREV643.sqlcbli`.
- Regressions: none found in full Cementera validation.

## Known Limits

This is a layout-artifact repair. It intentionally does not infer or alter ordinary COBOL level numbers.
