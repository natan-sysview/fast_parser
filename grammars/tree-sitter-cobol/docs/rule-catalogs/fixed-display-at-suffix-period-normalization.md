# Fixed DISPLAY AT Suffix Period Normalization

## Rule

`shift_display_at_suffix_period_inside_source`

## Purpose

Preserve a statement-closing period for fixed-layout COBOL screen `DISPLAY` statements when the period lands in physical column 73 and would otherwise be treated as suffix text outside the parser source area.

## Included Forms

```cobol
DISPLAY "..." AT 2015.
```

where:

- The file is parsed with `normal-fixed` layout normalization.
- The physical source area ends at column 72.
- The period is the only nonblank suffix character at column 73.
- The statement is a `DISPLAY` with an `AT` position.
- The display literal has at least one trailing fill space before the closing quote.

The parser input view removes one trailing fill space from the display literal so the final period moves into column 72.

## Excluded Forms

- Non-`DISPLAY` statements.
- `DISPLAY` statements without an `AT` position.
- Lines where the suffix has nonblank text after the period.
- Lines where the literal cannot donate one fill space before the closing quote.
- Source bytes are not rewritten; only parser input is normalized.

## Evidence

Baseline:

```text
runs/candidate_compare_current_cementera_numeric_abbreviated_or_continuation_tail_20260821.sqlite
```

Candidate:

```text
runs/candidate_compare_current_cementera_display_at_suffix_period_shift_20260821.sqlite
```

Result:

```text
Files: 4169
Parsed OK: 4169
Hard failures: 0
Files with ERROR: 12
ERROR nodes: 6
Files with MISSING: 0
MISSING nodes: 0
```

Improved files:

```text
PSTA025.sqlcbli
```

Regressions:

```text
0
```

Audit:

```text
audits/cementera_display_at_suffix_period_shift_20260821/issue_nodes.sqlite
audits/cementera_display_at_suffix_period_shift_20260821/error_families/
```

Decision:

```text
Stable for Cementera normal-fixed parser input.
```
