# DDS A-Spec Lines Normalization

## Purpose

Blank parser-input AS/400 DDS `A` specification rows embedded inside COBOL procedure text.

## Included Forms

- Fixed-layout physical lines shaped as five leading spaces, `A`, then DDS specification text.
- The full physical line is blanked before COBOL fixed-layout prefix stripping.

## Excluded Forms

- COBOL lines that do not carry the DDS `A` spec marker.
- Standalone DDS parsing.
- Source rewrites; original bytes are preserved.

## Local Shape

```cobol
     A          R CAB010
     A            RNMEMPRESA    35A  O    17
```

becomes blank parser-input lines.

## Evidence

- Baseline: `baselines/2026-08-21-before-cementera-dds-a-spec-lines-normalization/cobol_layout_normalization.py`
- Validation DB: `runs/candidate_compare_current_cementera_dds_a_spec_lines_normalization_20260821.sqlite`
- Audit DB: `audits/cementera_dds_a_spec_lines_normalization_20260821/issue_nodes.sqlite`
- Cementera result: `ERROR nodes 24 -> 22`, `MISSING nodes 0 -> 0`.
- Improved files: `PPACUC03.sqlcbli`, `PZARAG03.sqlcbli`.
- Regressions: none found in full Cementera validation.

## Known Limits

This normalization treats embedded DDS rows as non-COBOL noise for the COBOL parser. It does not attempt to model DDS syntax.
