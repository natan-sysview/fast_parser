# Rule Catalog: Burroughs Data Description Extensions

Status: implemented in experimental grammar.

## Goal

Parse narrowly scoped Burroughs/Unisys-style data-description forms observed in the local enterprise COBOL inventory:

- `WITH LOWER-BOUNDS`
- `REAL`

These forms currently create `ERROR` nodes in legacy `OBJECT` programs.

## Basis

This catalog is based on local inventory evidence from the COBOL parser lab:

- `WITH LOWER-BOUNDS`: 34 inventory files, all dirty before repair.
- `REAL` data-description entries: 16 inventory files, all dirty before repair.

The syntax appears in legacy generated/object COBOL sources under the `OBJECT` source group.

## Accepted Forms

```cobol
       01 A WITH LOWER-BOUNDS.
          05 B PIC 9.
```

```cobol
       77 A REAL.
```

## Excluded Forms

- General Burroughs object-computer hardware clauses such as `DISK SIZE ... MODULES`.
- Semantic meaning of lower-bound storage or real numeric representation.
- Treating arbitrary unknown words in data descriptions as valid clauses.
- Reclassifying `REAL` when it appears as an identifier outside a data-description clause position.

## Grammar Shape

- `burroughs_lower_bounds_clause`: `WITH LOWER-BOUNDS`
- `real_usage_clause`: `REAL`

Both are accepted only as data-description clauses.

## Corpus Coverage

- A group item with `WITH LOWER-BOUNDS` followed by a child elementary item.
- A level-77 item with `REAL`.

## Validation Plan

- Create a baseline before grammar changes.
- Generate parser.
- Run `tree-sitter test`.
- Build FastParse COBOL language extension.
- Validate the full COBOL inventory against `runs/candidate_compare_current_program_id_metadata_period_full.sqlite`.
- Audit rule matches and compare error/missing metrics.

## Validation Result

Validated on 2026-06-26 against 74,151 COBOL inventory files.

- `tree-sitter test`: 122/122.
- Parsed OK: 74,151.
- Hard failures: 0.
- Strict `ERROR` files: 32,638 before, 32,638 after.
- `ERROR` nodes: 35,520 before, 35,516 after.
- `MISSING` nodes: 18 before, 18 after.
- Files became clean: 0.
- Clean files that became dirty: 0.
- Error byte span increased by 64,263 bytes in one improved file (`P100_13MTP005`), while its `ERROR` node count fell from 6 to 2.

Full validation results are recorded in `runs/cobol_burroughs_data_description_repair_report.md`.
