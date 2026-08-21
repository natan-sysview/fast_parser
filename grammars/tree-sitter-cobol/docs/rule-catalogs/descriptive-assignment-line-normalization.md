# Descriptive Assignment Line Normalization

## Purpose

Blank parser-input lines that are descriptive business text accidentally placed in the COBOL procedure area without a comment marker.

## Included Forms

- Lines shaped like `<identifier> = <number> - <description> / <description>`.
- The whole physical line is blanked while preserving line length.

## Excluded Forms

- COBOL `COMPUTE`, `IF`, `MOVE`, or other valid statements.
- Ordinary comparisons without the descriptive `-` and `/` text shape.
- Source rewrites; original COBOL bytes are preserved.

## Local Shape

```cobol
ARTGRP02 = 04 - VASILHAME / 01 02 E 03 - COMODATO/EMPRESTIMO
```

becomes a blank parser-input line.

## Evidence

- Baseline: `baselines/2026-08-21-before-cementera-descriptive-assignment-line-normalization/cobol_layout_normalization.py`
- Validation DB: `runs/candidate_compare_current_cementera_descriptive_assignment_line_normalization_20260821.sqlite`
- Audit DB: `audits/cementera_descriptive_assignment_line_normalization_20260821/issue_nodes.sqlite`
- Cementera result: `ERROR nodes 30 -> 28`, `MISSING nodes 0 -> 0`.
- Improved files: `PVASI001.sqlcbli`, `PVASI001V.sqlcbli`.
- Regressions: none found in full Cementera validation.

## Known Limits

This is a client-corpus cleanup rule for non-COBOL descriptive text. It does not classify or preserve that text as a syntax node.
