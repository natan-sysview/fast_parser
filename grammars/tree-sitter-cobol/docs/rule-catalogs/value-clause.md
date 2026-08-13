# Rule Catalog: VALUE Clause

Status: implemented in experimental grammar.

## Goal

Improve COBOL data-description `VALUE` parsing for common enterprise forms.

The first target is level-88 condition values and data constants that list multiple literals separated by commas.

## Intended Nodes

Existing nodes are reused:

- `value_clause`
- `value_item`

## Accepted Forms

```cobol
       88 SW-VALIDAR-OK VALUE 'A','B','C','D'.
```

```cobol
       88 SW-VALIDAR-OK VALUE 'A', 'B', 'C',
                                  'D', 'E'.
```

```cobol
       88 MES VALUE 01 02 03 04 05 06 07 08 09 10 11 12.
```

```cobol
       88 WS-ESTATUS-INVALIDOS VALUE
          02 03 04 08 21 22 23 24 25 38 40 41 43 46 47.
```

```cobol
       88 WS-HORARIO-VALIDO VALUE 000000 THRU 005959,
          010000 THRU 015959,020000 THRU 025959,030000 THRU 035959.
```

The numeric list repair is scoped to condition-name entries (`level 88`) inside
COBOL data division entries. It keeps the public tree shape as
`data_description` -> `value_clause` -> `value_item`.

For condition-name values, numeric tokens intentionally do not include comma
characters. That allows comma-adjacent range lists such as
`015959,020000 THRU 025959` to parse as two `value_item` nodes instead of one
oversized numeric token.

## Excluded From First Batch

- Full semantic validation of level-88 condition names.
- Changing string continuation scanner behavior.
- Multiline string continuation repair.
- Literal values split by invalid source bytes or unterminated quoted strings.
- Changing the global COBOL `integer` token, which still accepts commas outside
  this level-88 condition-name path.

## Baseline Metrics To Beat

After the `EXEC CICS` repair:

- Files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- `ERROR` nodes: 79,784.
- `MISSING` nodes: 2,340.
- `DATA_DESCRIPTION` family: 13,109 `ERROR` nodes.

## Success Criteria

- `tree-sitter generate` succeeds.
- Corpus examples for comma-separated value lists pass.
- Full inventory diagnostics has zero hard failures.
- Net `ERROR` count does not increase.
- Regression set is saved and inspected before promotion.

## Validation Result

Validated on 2026-06-25 against the COBOL inventory of 74,151 non-JCL files.

- Parsed OK: 74,151.
- Hard failures: 0.
- Files improved: 6.
- Files regressed: 0.
- `ERROR` nodes: 79,784 before, 79,778 after.
- `MISSING` nodes: 2,340 before, 2,339 after.
- Binary MessagePack bytes: 22,953,736,424.
- SQLite integrity check: `ok`.

The impact is small but safe, so the rule remains in the experimental grammar.

## Artifacts

- Diagnostics DB: `runs/candidate_compare_current_value_clause_full.sqlite`.
- Binary validation DB: `runs/cobol_fastparse_binary_validation_value_clause_full.sqlite`.
- Report: `runs/cobol_value_clause_repair_report.md`.
- Comparison audit: `audits/value_clause_repair/`.
- Residual family audit: `audits/error_family_classification_after_value_clause/`.

## Latest Validation: Condition-Name Range Lists

Validated on 2026-08-13 against 74,242 COBOL files with `normal-fixed` layout
normalization.

- Corpus: 185/185 passed.
- Parsed OK: 74,242.
- Hard failures: 0.
- `ERROR` nodes: 4,231 before, 4,231 after.
- `MISSING` nodes: 34 before, 2 after.
- Files regressed: 0.
- The repaired file was `P012_13MTP013`, which moved from 32 `MISSING` nodes
  to 0 while keeping the same `ERROR` count.

Artifacts:

- Report: `runs/cobol_condition_name_range_list_token_repair_report.md`.
- Validation DB:
  `runs/candidate_compare_current_condition_name_range_list_token_full_inventory_20260813.sqlite`.
- Audit DB:
  `audits/profile_issue_nodes_current_condition_name_range_list_token_full_inventory_20260813/profile_issue_nodes.sqlite`.
