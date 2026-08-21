# Pointer Value NULLS

Status: stable experimental grammar rule.

## Goal

Parse COBOL data descriptions that initialize pointer items with the figurative
constant `NULLS`.

The motivating real shape is:

```text
05 WS-PTR POINTER VALUE NULLS.
```

Before this rule, `NULLS` could be tokenized as `NULL` plus a trailing `S`,
which created `ERROR` nodes in otherwise normal data descriptions.

## Included Forms

- `VALUE NULL`
- `VALUE NULLS`
- Case variants already supported by the grammar token style:
  - `null`, `Null`, `NULL`
  - `nulls`, `Nulls`, `NULLS`

## Excluded Forms

- Semantic pointer validation.
- Dialect-specific pointer storage semantics.
- Broader rewriting of value literals.
- Treating arbitrary words ending in `S` as figurative constants.

## Local Behavior

`NULLS` is accepted by the existing `TOK_NULL` terminal and therefore remains
inside the existing `value_clause` and `value_item` parse shape. No new public
node is introduced.

## Corpus Examples Covered

- `test/corpus/data_description.txt`: `pointer value nulls`

## Validation Result

Validated on 2026-08-14 against the COBOL inventory of 74,242 files.

- Corpus: 201/201 passing.
- Parsed OK: 74,242.
- Hard failures: 0.
- Files with `ERROR`: 2,249 before, 2,224 after.
- `ERROR` nodes: 2,622 before, 2,597 after.
- Files with `MISSING`: 0 before, 0 after.
- `MISSING` nodes: 0 before, 0 after.
- Improved files: 25.
- Regressed files: 0.

The inventory scan found 27 files containing `VALUE NULLS`. Of those, 25 had a
single `ERROR` node before this rule and now parse without that error. The
remaining 2 were already clean.

## Artifacts

- Report: `runs/cobol_pointer_value_nulls_repair_report.md`
- Validation DB: `runs/candidate_compare_current_pointer_value_nulls_20260814.sqlite`
- Audit: `audits/pointer_value_nulls_20260814/`
- Baseline: `baselines/2026-08-14-after-pointer-value-nulls/`

Decision: stable experimental rule.
