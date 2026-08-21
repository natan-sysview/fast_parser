# statement-period-before-area-a-header-normalization

## Purpose

Close legacy procedure statements in parser input when a new Area A paragraph header follows without a period.

## Basis

Cementera contains screen code such as:

```cobol
DISPLAY "F2=Volta   F3=abandona " AT 2122
*
PROCESSAMENTO.
```

The source omits the statement period before a paragraph header. The grammar alone cannot reliably distinguish a paragraph header from a continued display operand because it does not see fixed columns. The layout normalizer does see columns.

## Included Forms

- Layout-normalized fixed files.
- A next non-comment line that looks like a paragraph header starting in Area A.
- A previous non-comment line that starts with `DISPLAY`, `MOVE`, `PERFORM`, `GOBACK`, `GO`, or `GOTO`.
- A previous display continuation line that starts with a quoted literal and contains `AT`.
- A previous display continuation line that ends with `AT <position>`.
- A previous display attribute continuation line that starts with `WITH` and contains a screen attribute.
- Previous line has no final period.
- For fixed-short files that are not fully normalized by `normal-fixed`, only this display/header parser-input view is applied; suffix trimming and prefix blanking remain unchanged.

## Excluded Forms

- Non-layout-normalized parser input.
- Headers outside Area A.
- Statement families outside the audited boundary forms.
- Original source bytes; only parser input is closed with a synthetic period.

## Normalizer Shape

`tools/cobol_layout_normalization.py` inserts a period at the end of the previous parser-input line before joining the normalized lines. The same local statement/header view is allowed when the file has fixed columns with indicator column 7 and source start column 8, even if full layout normalization is not applied.

## Audit Result

Cementera validation after the first full-layout implementation:

- DB: `runs/candidate_compare_current_cementera_display_period_normalizer_20260821.sqlite`
- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- Files with ERROR: 145
- ERROR nodes: 114
- Files with MISSING: 0
- MISSING nodes: 0
- Improved files: 32
- Regressions: 0 files.

Cementera validation after enabling the same display/header view for fixed-short parser input:

- DB: `runs/candidate_compare_current_cementera_display_period_fixed_short_view_20260821.sqlite`
- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- Files with ERROR: 110
- ERROR nodes: 76
- Files with MISSING: 0
- MISSING nodes: 0
- Improved files: 38
- Regressions: 0 files.

Cementera validation after extending the Area A boundary closure to audited `PERFORM`, `GOBACK`, `GO`, and display-continuation forms:

- Baseline: `baselines/before_cementera_statement_period_before_area_a_header_20260821/`
- DB: `runs/candidate_compare_current_cementera_statement_period_before_area_a_header_v2_20260821.sqlite`
- Audit: `audits/cementera_statement_period_before_area_a_header_v2_20260821/`
- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- Files with ERROR: 66
- ERROR nodes: 61
- Files with MISSING: 0
- MISSING nodes: 0
- Improved files: 15 versus `candidate_compare_current_cementera_display_period_fixed_short_view_20260821.sqlite`
- Regressions: 0 files.

Cementera validation after recognizing inline paragraph exits such as `001-FIM. EXIT.` as Area A headers for the same parser-input closure:

- Baseline: `baselines/before_cementera_inline_exit_header_period_view_20260821/`
- DB: `runs/candidate_compare_current_cementera_inline_exit_header_period_view_20260821.sqlite`
- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- Files with ERROR: 52
- ERROR nodes: 47
- Files with MISSING: 0
- MISSING nodes: 0
- Improved files: 14 versus `candidate_compare_current_cementera_statement_period_before_area_a_header_v2_20260821.sqlite`
- Regressions: 0 files.

Cementera validation after adding `MOVE` as an audited statement-boundary form before Area A paragraph headers:

- Baseline: `baselines/before_cementera_move_period_before_area_a_header_20260821/`
- DB: `runs/candidate_compare_current_cementera_move_period_before_area_a_header_20260821.sqlite`
- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- Files with ERROR: 44
- ERROR nodes: 39
- Files with MISSING: 0
- MISSING nodes: 0
- Improved files: 1 versus `candidate_compare_current_cementera_stable_after_level88_revert_20260821.sqlite`
- Regressions: 0 files.
