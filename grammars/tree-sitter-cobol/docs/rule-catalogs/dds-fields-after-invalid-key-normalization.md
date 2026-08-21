# DDS Fields After INVALID KEY Normalization

## Purpose

Blank parser-input DDS-style field rows accidentally embedded inside a COBOL `READ ... INVALID KEY` branch.

## Included Forms

- After a physical line containing `READ ... INVALID KEY`.
- Consecutive rows shaped like `<field-name> <number>A` or `<field-name> <number>S`.
- The rows are blanked while preserving line length.

## Excluded Forms

- Standalone `.pf` DDS/copybook files.
- DDS rows outside a `READ ... INVALID KEY` branch.
- Valid COBOL data description entries.
- Source rewrites; original COBOL bytes are preserved.

## Local Shape

```cobol
READ DSFCK002 INVALID KEY
       CDCATG 1A
       CDSEGM 1A
    GO GRAVA-DSFCK002
END-READ.
```

The DDS field rows become blank parser-input lines.

## Evidence

- Baseline: `baselines/2026-08-21-before-cementera-dds-fields-after-invalid-key-normalization/cobol_layout_normalization.py`
- Validation DB: `runs/candidate_compare_current_cementera_dds_fields_after_invalid_key_normalization_20260821.sqlite`
- Audit DB: `audits/cementera_dds_fields_after_invalid_key_normalization_20260821/issue_nodes.sqlite`
- Cementera result: `ERROR nodes 28 -> 27`, `MISSING nodes 0 -> 0`.
- Improved file: `PSFCK002.sqlcbli`.
- Regressions: none found in full Cementera validation.

## Known Limits

This normalization treats those rows as embedded non-COBOL noise. It does not parse DDS as COBOL.
