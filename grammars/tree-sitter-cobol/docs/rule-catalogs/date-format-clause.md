# DATE FORMAT Clause

## Rule Name

`date_format_clause`

## Purpose

Recognize COBOL data-description clauses of the form `DATE FORMAT <format-word>` after a `PIC`/`PICTURE` clause.

This syntax appears in the local COBOL inventory as:

```cobol
05 WSV-FECHA PIC 9(08) DATE FORMAT YYYYXXXX.
```

## Basis

The rule is based on observed enterprise COBOL sources in the lab inventory. It is implemented as a single external token nested under `picture_clause` to avoid exposing broad standalone `DATE` or `FORMAT` alternatives in `DATA DIVISION`, which previously caused large parse regressions.

## Included Forms

- `DATE FORMAT YYYYXXXX`
- Mixed-case variants such as `date format yyyymmdd`
- Format words composed of letters, digits, or hyphen
- A following normal data-description period
- Fixed-format line suffix text after the period when it is already handled by existing extras

## Excluded Forms

- `DATE FORMAT` text inside comments or string literals
- Data names such as `WS-DATE-FORMAT`
- Any standalone `DATE` clause without `FORMAT`
- Any semantic validation of the actual date-picture pattern
- General-purpose `FORMAT` clauses outside data descriptions

## Local Syntactic Shape

The rule is available only immediately after a `PIC`/`PICTURE` string:

```text
data_description
  picture_clause
    picture_9
    date_format_clause
```

The external scanner consumes exactly:

```text
DATE <spaces> FORMAT <spaces> <format-word>
```

It leaves the terminating period to the existing data-description period rule.

## Corpus Coverage

- Minimal positive numeric data description.
- Lowercase positive variant.
- Fixed-format suffix variant.
- Negative string literal containing `DATE FORMAT`.
- Negative data name containing `DATE-FORMAT`.

## Known Limits

The grammar does not validate whether the date format is accepted by a specific COBOL compiler family. Dialect-specific validation belongs in profile/audit tooling.

## Audit Summary

Candidate accepted for this repair batch: `current_date_format_clause_v4`.

- Corpus: 148/148.
- Inventory files validated: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- Files with Tree-sitter `ERROR`: 10,656, down from 10,666.
- `ERROR` nodes: 11,711, down from 11,723.
- Files with `MISSING`: 1, unchanged.
- `MISSING` nodes: 1, unchanged.
- Files with lower `ERROR` count: 11.
- Files that became clean: 10.
- Files with higher `ERROR` count: 0.
- `date_format_clause` nodes found: 12 nodes in 11 files.
- Heuristic `DATE FORMAT` review: 27 text hits in 20 files; 12 syntax candidates, 14 comments, 1 string literal.
- Confirmed syntax candidates without node: 0.
- Validation DB: `runs/candidate_compare_current_date_format_clause_v4_full.sqlite`.
- Rule audit: `audits/date_format_clause_v4/date_format_clause_audit.md`.
