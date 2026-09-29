# PLSQL Round 36-37 - Pure PL/SQL Scope and AST Cleanup

## Goal

Keep the experimental PL/SQL grammar focused on pure PL/SQL and DDL after
Oracle Forms exports were reclassified in the shared inventory as
`plsql-oracle-formas`.

## Included Syntax

- Standard PL/SQL packages, package bodies, standalone procedures, standalone
  functions, and nested procedures/functions.
- Create table DDL and companion DDL already covered by the `CR` subtype.
- Narrow legacy recovery nodes for malformed PL/SQL artifacts that remain in
  the pure PL/SQL inventory.
- Hidden helper tails used internally by truncated package/procedure recovery.

## Excluded Syntax

- Converted Oracle Forms trigger/export syntax from `plsql_to_java` paths.
- Forms-specific glued keyword recovery.
- Forms pseudo datatypes and Forms trigger-body shortcuts.
- D2K program unit comment recovery.

## Grammar Changes

- Removed active Oracle Forms alternatives from `source_file`,
  `create_procedure`, parameter identifiers, datatype alternatives, conflicts,
  and extras.
- Removed Oracle Forms corpus cases from the active PL/SQL smoke corpus.
- Hid internal truncated procedure/package tail helpers:
  `_legacy_truncated_procedure_definition_tail` and
  `_legacy_truncated_procedure_declaration_tail`.
- Removed conflicts that became unnecessary after the Forms purge and nested
  subprogram refinements.

## AST Contract

Key nodes keep stable fields for downstream analysis:

- `create_table.table_name`
- `create_package.package_name`
- `create_package_body.package_name`
- `create_procedure.prc_name`
- `create_procedure.schema_name`
- `create_function.fnc_name`
- `create_function.schema_name`
- `procedure_definition.prc_name`
- `function_definition.fnc_name`
- `nested_procedure_definition.prc_name`
- `nested_function_definition.fnc_name`

## Validation

Round 37 used the shared inventory filtered by `type = 'plsql'`, so the
reclassified Oracle Forms files were not part of pure PL/SQL validation.

- Output DB: `runs/plsql_native_validation_round37_hidden_truncated_tail_helpers_threads8.sqlite`
- Threads: 8
- Inventory files: 11,021
- Inventory lines: 4,369,801
- Hard failures: 0
- Files with `ERROR`: 0
- Total `ERROR` nodes: 0
- Files with `MISSING`: 0
- Total `MISSING` nodes: 0
- Total AST nodes: 38,926,730
- Encoding normalized: 1,268
- Wall time: 19.60 seconds

Subtype summary:

| Subtype | Files | Lines | ERROR nodes | MISSING nodes |
| --- | ---: | ---: | ---: | ---: |
| CR | 6,794 | 244,515 | 0 | 0 |
| FNC | 467 | 56,991 | 0 | 0 |
| PKB | 1,426 | 3,528,442 | 0 | 0 |
| PKS | 1,246 | 223,844 | 0 | 0 |
| PRC | 1,088 | 316,009 | 0 | 0 |

The corpus suite passed 159/159. Tree-sitter still reports a slow-parse notice
for the first `create_table` corpus fixture; this is a performance refinement
candidate, not a parser correctness warning.

## Legacy Node Audit

- Output DB: `audits/round37_hidden_truncated_tail_helpers/legacy_node_quality_audit.sqlite`
- Inventory files: 11,021
- Audited OK: 11,021
- Audit failures: 0
- Files with visible `legacy_*` nodes: 18
- Total visible `legacy_*` nodes: 19
- Wall time: 21.10 seconds

Remaining visible legacy nodes are intentional markers for malformed or
truncated source artifacts still present in the pure PL/SQL corpus.

| Node type | Files | Nodes | Subtypes |
| --- | ---: | ---: | --- |
| `legacy_package_name_repeat` | 5 | 5 | PKS |
| `legacy_pisr_layout_export_file` | 4 | 4 | PRC |
| `legacy_procedure_name_prefix` | 2 | 2 | PRC |
| `legacy_dml_missing_comma_column` | 1 | 1 | PKB |
| `legacy_embedded_non_plsql_block` | 1 | 1 | PKB |
| `legacy_fetch_exit_without_separator` | 1 | 1 | PRC |
| `legacy_java_style_assignment_declaration` | 1 | 1 | PKB |
| `legacy_parenthesized_with_select_statement` | 1 | 1 | PKB |
| `legacy_plsql_block_statement_with_stray_suffix` | 1 | 1 | PKB |
| `legacy_truncated_package_body_file` | 1 | 1 | PKB |
| `legacy_truncated_package_spec_file` | 1 | 1 | PKS |

## Promotion Decision

The grammar is ready to promote to `grammars/tree-sitter-plsql` after creating
a backup of the productive grammar and preserving the Round 37 baseline.
