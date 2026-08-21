# display-mixed-positioned-groups

## Purpose

Recognize COBOL screen `DISPLAY` statements that mix positioned operand groups where some operands use `WITH ... AT` and later operands use `AT ... WITH`.

## Basis

Cementera screen programs contain multi-line `DISPLAY` statements such as:

```cobol
DISPLAY
    "Header" WITH REVERSE-VIDEO AT 0715
    "Body" AT 0917
    FIELD-A AT 1101 WITH HIGHLIGHT.
```

The prior grammar accepted `WITH ... AT` for a single display group and accepted repeated `AT ... WITH` groups, but not both styles in one `DISPLAY`.

## Included Forms

- One or more positioned display groups in a single `DISPLAY`.
- Groups where the screen attribute appears before the `AT` clause.
- Groups where the `AT` clause appears before a `WITH` clause.
- Literal and identifier operands already covered by `_x`.

## Excluded Forms

- Arbitrary recovery for malformed display text.
- Semantic validation of screen coordinates or attributes.
- Source repair for truncated literals; those remain diagnostics.

## Grammar Shape

`_display_body` now accepts repeated hidden `_display_positioned_group_variant` entries. The new hidden `_display_attributed_positioned_group` requires `display_with_before_at_clause` followed by `at_line_column`, so existing non-positioned `WITH` forms still use the previous rule.

## Corpus

- `test/corpus/display_tolerances.txt`
  - `display mixed attributed positioned groups`

## Audit Result

Cementera validation:

- Baseline: `baselines/before_cementera_display_mixed_positioned_groups_20260821/`
- DB: `runs/candidate_compare_current_cementera_display_mixed_positioned_groups_20260821.sqlite`
- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- Files with ERROR: 48
- ERROR nodes: 43
- Files with MISSING: 0
- MISSING nodes: 0
- Improved files: 4 versus `candidate_compare_current_cementera_inline_exit_header_period_view_20260821.sqlite`
- Regressions: 0 files.
- Corpus: 290/290 passing.
