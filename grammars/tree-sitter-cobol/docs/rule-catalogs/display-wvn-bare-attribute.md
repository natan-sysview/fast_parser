# display-wvn-bare-attribute

## Purpose

Recognize Cementera legacy screen `DISPLAY` statements that use `WVN` as a bare video/display attribute after an `AT` position.

## Basis

Cementera contains forms such as:

```cobol
DISPLAY "< S > Suco    " AT 2060 WVN.
DISPLAY WVI "TECLE ..." AT 1523 WVN.
```

The prior grammar parsed the display operand and `AT` coordinate but treated trailing `WVN` as an unexpected token.

## Included Forms

- `WVN` immediately after a positioned display group.
- Literal or identifier operands already accepted by existing display rules.
- The rule is case-insensitive.

## Excluded Forms

- Arbitrary identifiers as display attributes.
- `WVI` as a keyword; it remains a normal operand/identifier.
- Semantic validation of the terminal attribute meaning.

## Grammar Shape

Adds named `legacy_display_bare_attr` for `WVN` and allows it after positioned display groups. The token is deliberately specific to avoid swallowing ordinary identifiers after `AT`.

## Corpus

- `test/corpus/display_tolerances.txt`
  - `display positioned group with bare wvn attribute`

## Audit Result

Cementera validation:

- Baseline: `baselines/before_cementera_display_wvn_bare_attribute_20260821/`
- DB: `runs/candidate_compare_current_cementera_display_wvn_bare_attribute_20260821.sqlite`
- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- Files with ERROR: 46
- ERROR nodes: 41
- Files with MISSING: 0
- MISSING nodes: 0
- Improved files: 2 versus `candidate_compare_current_cementera_display_mixed_positioned_groups_20260821.sqlite`
- Regressions: 0 files.
- Corpus: 291/291 passing.
