# Abbreviated NOT List Continuation Normalization

## Rule name

`abbreviated_not_list_continuation`

## Purpose

Normalize continued `IF <var> NOT = ...` literal lists where continuation lines contain only quoted literals joined by `AND`, but omit the leading `AND` that connects the continuation back to the prior physical line.

## Included forms

- A previous line matching an `IF <identifier> NOT = ... AND "<literal>"` condition.
- Following physical lines matching only:

```text
\s+"<literal>"(\s+AND\s+"<literal>")*\s*
```

- At least four leading spaces are available before the first literal.

## Excluded forms

- Any continuation not immediately following the detected `IF ... NOT =` list.
- Lines containing statements, identifiers, or non-literal expressions.
- Non-`NOT =` conditions.

## Local syntactic shape

The normalizer inserts `AND ` by consuming four leading spaces before the first literal, preserving physical line length.

## Evidence

Baseline:

```text
baselines/2026-08-21-before-cementera-abbreviated-not-list-continuation-normalization/cobol_layout_normalization.py
```

Validation DB:

```text
runs/candidate_compare_current_cementera_abbreviated_not_list_continuation_normalization_20260821.sqlite
```

Audit DB:

```text
audits/cementera_abbreviated_not_list_continuation_normalization_20260821/issue_nodes.sqlite
```

Scope search found two matching continuation lines, both in:

```text
PRV10015.sqlcbli
```

## Result

Compared with `current_cementera_mixed_quote_display_continuation_normalization_20260821`:

- Files: `4169`
- Parsed OK: `4169`
- Hard failures: `0`
- Files with ERROR: `17 -> 16`
- ERROR nodes: `11 -> 10`
- Files with MISSING: `0 -> 0`
- MISSING nodes: `0 -> 0`
- Improved file: `PRV10015.sqlcbli`
- Regressions: none observed

## Known semantic limits

This is intentionally narrower than the earlier broad abbreviated-literal continuation experiment, which regressed unrelated files. It only handles a detected `IF ... NOT =` literal-list continuation.
