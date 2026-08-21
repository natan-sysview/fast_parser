# if-not-literal-condition

## Purpose

Recover legacy `IF <identifier> NOT <literal>` conditions as not-equal comparisons.

## Basis

Cementera contains:

```cobol
IF FS1 NOT "00"
```

where surrounding code indicates a not-equal file-status check.

## Included Forms

- `IF <expr> NOT <literal>`
- String and figurative literal right operands supported by the existing abbreviated literal operand rule.

## Excluded Forms

- Global `NOT <literal>` comparisons outside `if_header`.
- Boolean negation forms such as `IF NOT A`.
- Compute or arithmetic expression changes.

## Grammar Shape

Adds `legacy_not_literal_condition` as an `if_header` condition alternative only.

## Corpus

- `abbreviated_comparison_continuation.txt`
  - `legacy not literal condition`

## Audit Result

Validation `runs/candidate_compare_current_cementera_if_not_literal_20260821.sqlite`:

- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- ERROR nodes: 152, down from 153
- MISSING nodes: 0, unchanged
- Improved file: `PCLISKU05.sqlcbli`
- Regressions: 0
