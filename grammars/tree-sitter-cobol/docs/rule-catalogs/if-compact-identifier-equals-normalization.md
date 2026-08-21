# IF Compact Identifier Equals Normalization

## Purpose

Normalize parser input for singleton legacy typo forms like `IF A=B = literal` when the same source text also contains the valid COBOL data-name `A-B`.

## Included Forms

- `IF <prefix>=<suffix> = <numeric-literal>`
- `IF <prefix>=<suffix> = "<literal>"`
- `IF <prefix>=<suffix> = '<literal>'`
- Only when `<prefix>-<suffix>` appears as a data-name in the same parser input text.

## Excluded Forms

- General equality expressions.
- Identifiers where the hyphenated data-name is not present in the same file.
- Non-`IF` statements.
- Source rewrites; the original COBOL bytes are preserved.

## Local Shape

The parser input view replaces the first compact `=` with `-`, preserving line length:

```cobol
IF LK=CDLOC = 20
```

becomes:

```cobol
IF LK-CDLOC = 20
```

## Evidence

- Baseline: `baselines/2026-08-21-before-cementera-if-compact-equals-normalization/cobol_layout_normalization.py`
- Validation DB: `runs/candidate_compare_current_cementera_if_compact_equals_normalization_20260821.sqlite`
- Audit DB: `audits/cementera_if_compact_equals_normalization_20260821/issue_nodes.sqlite`
- Cementera result: `ERROR nodes 34 -> 33`, `MISSING nodes 0 -> 0`.
- Improved file: `PPISNFIS10.sqlcbli`.
- Regressions: none found in full Cementera validation.

## Known Limits

This is a typo-tolerant layout normalization, not a COBOL grammar rule. It is intentionally guarded by same-file evidence of the hyphenated identifier to avoid changing valid comparisons.
