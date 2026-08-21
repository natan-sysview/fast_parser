# Date Placeholder Value Normalization

## Rule name

`date_placeholder_value`

## Purpose

Normalize data-description filler values where a visual date placeholder appears as bare text after `VALUE`, for example `VALUE XX.XX.XXXX`. COBOL requires this placeholder to be a literal for the data-description entry to parse.

## Included forms

- A full physical line matching:

```text
\s+03\s+FILLER\s+PIC\s+X\([^)]*\)\s+VALUE\s+XX\.XX\.XXXX\s*
```

## Excluded forms

- Already quoted literals.
- Non-`FILLER` data items.
- Placeholders other than `XX.XX.XXXX`.
- Procedure statements.

## Local syntactic shape

The normalizer quotes the placeholder as `"XX.XX.XXXX"` by consuming two spaces before the placeholder, preserving the physical line length.

## Evidence

Baseline:

```text
baselines/2026-08-21-before-cementera-date-placeholder-value-normalization/cobol_layout_normalization.py
```

Validation DB:

```text
runs/candidate_compare_current_cementera_date_placeholder_value_normalization_20260821.sqlite
```

Audit DB:

```text
audits/cementera_date_placeholder_value_normalization_20260821/issue_nodes.sqlite
```

Scope search found one matching line in:

```text
VIAGEM42.sqlcbli
```

## Result

Compared with `current_cementera_split_hyphenated_label_normalization_20260821`:

- Files: `4169`
- Parsed OK: `4169`
- Hard failures: `0`
- Files with ERROR: `20 -> 19`
- ERROR nodes: `14 -> 13`
- Files with MISSING: `0 -> 0`
- MISSING nodes: `0 -> 0`
- Improved file: `VIAGEM42.sqlcbli`
- Regressions: none observed

## Known semantic limits

This only handles the observed visual date placeholder in `FILLER` data descriptions. It is not a general literal-inference rule for arbitrary bare words after `VALUE`.
