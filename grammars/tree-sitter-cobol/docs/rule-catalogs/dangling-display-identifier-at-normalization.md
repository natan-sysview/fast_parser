# Dangling DISPLAY Identifier AT Normalization

## Purpose

Normalize parser input for legacy screen statements where a `DISPLAY` of an identifier ends with a dangling `AT` and the next code line starts a separate COBOL statement.

## Included Forms

- `DISPLAY <identifier> AT`
- `DISPLAY <identifier> OF <identifier> AT`
- The next non-comment code line must start with a known COBOL statement keyword.

## Excluded Forms

- Literal display continuations such as `DISPLAY "text" AT` followed by a coordinate variable.
- Multi-line screen display forms that continue with a position expression.
- Source rewrites; original COBOL bytes are preserved.

## Local Shape

The parser input view blanks the dangling `AT`, preserving line length:

```cobol
DISPLAY CHAVE-LANC AT
ADD 1 TO KLIDO
```

becomes:

```cobol
DISPLAY CHAVE-LANC
ADD 1 TO KLIDO
```

## Evidence

- Baseline: `baselines/2026-08-21-before-cementera-dangling-display-identifier-at-normalization/cobol_layout_normalization.py`
- Validation DB: `runs/candidate_compare_current_cementera_dangling_display_identifier_at_normalization_20260821.sqlite`
- Audit DB: `audits/cementera_dangling_display_identifier_at_normalization_20260821/issue_nodes.sqlite`
- Cementera result: `ERROR nodes 33 -> 32`, `MISSING nodes 0 -> 0`.
- Improved file: `CONV101.cblile`.
- Regression guard: `PPOCKSTAHD.sqlcbli` literal display continuations remained clean.
- Regressions: none found in full Cementera validation.

## Known Limits

This is a typo-tolerant parser input normalization for incomplete screen syntax. It does not attempt to infer missing screen coordinates.
