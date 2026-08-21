# MOVE Literal TO Before Header Normalization

## Purpose

Close parser-input `MOVE` statements whose literal and `TO ... PERFORM ...` continuation are immediately followed by a paragraph header.

## Included Forms

- A paragraph header follows the current line.
- The current line starts with `TO ` and contains ` PERFORM `.
- The two previous physical lines are exactly `MOVE` and a quoted literal.
- The current line is closed with a period in the parser input view.

## Excluded Forms

- Ordinary `TO ... PERFORM ...` lines not part of `MOVE` literal continuation.
- Lines before headers without the exact `MOVE` + literal context.
- Source rewrites; original COBOL bytes are preserved.

## Local Shape

```cobol
MOVE
"QUE O QUE ESTA OCORRENDO."
TO WREL8-B PERFORM 200-IMPRIME-ERRO THRU 200-FIM
160000-FIM. EXIT.
```

becomes:

```cobol
MOVE
"QUE O QUE ESTA OCORRENDO."
TO WREL8-B PERFORM 200-IMPRIME-ERRO THRU 200-FIM.
160000-FIM. EXIT.
```

## Evidence

- Baseline: `baselines/2026-08-21-before-cementera-move-literal-to-before-header-normalization/cobol_layout_normalization.py`
- Validation DB: `runs/candidate_compare_current_cementera_move_literal_to_before_header_normalization_20260821.sqlite`
- Audit DB: `audits/cementera_move_literal_to_before_header_normalization_20260821/issue_nodes.sqlite`
- Cementera result: `ERROR nodes 26 -> 24`, `MISSING nodes 0 -> 0`.
- Improved files: `PPREV508.sqlcbli`, `PPREV508YY.sqlcbli`.
- Regressions: none found in full Cementera validation.

## Known Limits

This normalization recovers a specific unterminated multiline `MOVE` shape. It is not a generic rule for all `TO ... PERFORM` lines.
