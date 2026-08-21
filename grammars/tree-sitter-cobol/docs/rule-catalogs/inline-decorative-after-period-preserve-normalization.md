# Inline Decorative After Period Preserve Normalization

## Purpose

Blank decorative inline comments that appear after a completed COBOL statement period while preserving physical line length.

## Included Forms

- A period followed by spaces and a decorative marker of three or more asterisks.
- Example: `.    ****AQUI`.
- Only the decorative suffix is blanked in the parser input view.

## Excluded Forms

- Full-line comments.
- COBOL text before the statement period.
- Source rewrites; original bytes are preserved.

## Local Shape

```cobol
OPEN INPUT DPREV010.    ****AQUI
```

becomes:

```cobol
OPEN INPUT DPREV010.
```

with trailing spaces preserved.

## Evidence

- Baseline: `baselines/2026-08-21-before-cementera-inline-decorative-after-period-preserve-normalization/cobol_layout_normalization.py`
- Validation DB: `runs/candidate_compare_current_cementera_inline_decorative_after_period_preserve_normalization_20260821.sqlite`
- Audit DB: `audits/cementera_inline_decorative_after_period_preserve_normalization_20260821/issue_nodes.sqlite`
- Cementera result: `ERROR nodes 22 -> 21`, `MISSING nodes 0 -> 0`.
- Improved file: `PDCTB0003.sqlcbli`.
- Regressions: none found in full Cementera validation.

## Known Limits

This is parser-input cleanup for decorative suffix comments. It intentionally does not reinterpret arbitrary inline text as comments.
