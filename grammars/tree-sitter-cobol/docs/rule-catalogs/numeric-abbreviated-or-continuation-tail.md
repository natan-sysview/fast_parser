# Numeric Abbreviated OR Continuation Tail

## Rule

`abbreviated_literal_tail`

## Purpose

Support COBOL abbreviated comparison lists where an `OR` at the end of a physical line continues with a numeric literal on the next line.

Example shape:

```cobol
IF CDPRO = 116 OR 134 OR
           234 OR > 125
   CONTINUE
END-IF.
```

## Included Forms

- Same-line numeric tails after an initial comparison, for example `OR 0500`.
- Line-broken `OR` followed by an indented numeric literal on the next physical line.
- Existing abbreviated range operators after the numeric list, for example `OR > 125` and `AND < 166`.

## Excluded Forms

- Line-broken `AND` followed by a numeric literal. This is intentionally excluded because Cementera has fixed-layout lines where an `AND` at end of line can be followed by a physical line prefix such as `02`, which must not be consumed as a comparison literal.
- Numeric-leading identifiers such as `054-EVENTO`.
- Condition names or other identifiers after `AND` / `OR`.

## Corpus

- `test/corpus/abbreviated_comparison_continuation.txt`
- `test/corpus/hyphenated_data_names.txt`

Corpus result:

```text
Total parses: 296
Successful parses: 296
Failed parses: 0
```

## Cementera Validation

Baseline:

```text
runs/candidate_compare_current_cementera_abbreviated_not_list_continuation_normalization_20260821.sqlite
```

Candidate:

```text
runs/candidate_compare_current_cementera_numeric_abbreviated_or_continuation_tail_20260821.sqlite
```

Result:

```text
Files: 4169
Parsed OK: 4169
Hard failures: 0
Files with ERROR: 13
ERROR nodes: 7
Files with MISSING: 0
MISSING nodes: 0
```

Improved files:

```text
PESTSLD200.sqlcbli
PMOSTVAS05.sqlcbli
TOTCLI11.sqlcbli
```

Regressions:

```text
0
```

Audit:

```text
audits/cementera_numeric_abbreviated_or_continuation_tail_20260821/issue_nodes.sqlite
audits/cementera_numeric_abbreviated_or_continuation_tail_20260821/error_families/
```

Decision:

```text
Stable for Cementera; keep `AND` line-broken numeric tails out of scope until a safe physical-layout guard is available.
```
