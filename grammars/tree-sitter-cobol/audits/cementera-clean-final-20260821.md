# Cementera Clean Final - 2026-08-21

## Scope

Inventory-backed Cementera COBOL universe after removing `PINDPIS39A.sqlcbli` from the lab inventory.

## Final FastParse Control

Command mode:

- FastParse local build
- COBOL language extension local build
- `ParseBytes`
- diagnostics output
- `auto_safe` normalization
- 12 workers

Result:

| Metric | Value |
| --- | ---: |
| files | 4,146 |
| ok | 4,146 |
| hard_failures | 0 |
| has_errors_files | 0 |
| files_with_ERROR | 0 |
| ERROR_nodes | 0 |
| files_with_MISSING | 0 |
| MISSING_nodes | 0 |
| error_bytes | 0 |
| lines | 2,300,953 |
| bytes | 93,085,133 |
| nodes | 10,466,880 |
| seconds | 1.642 |

## Inventory Control

Current view:

| Metric | Value |
| --- | ---: |
| rows | 4,146 |
| has_errors | 0 |
| error_nodes | 0 |
| missing_nodes | 0 |

Current run row:

| selected_files | clean_files | files_with_has_errors | error_nodes | files_with_missing | missing_nodes |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4,146 | 4,146 | 0 | 0 | 0 | 0 |

## Validation

- `tree-sitter generate`
- `tree-sitter test --rebuild`: `300/300`
- `cmake --build build-normalizer-0.1.1 --config Release`
- `python3 -m unittest tests.test_tsmp_contract.TsmpContractTests.test_cobol_auto_safe_normalization_handles_fixed_layout_view_repairs`: OK

## Inventory Updates

Removed from the lab inventory only:

- `PINDPIS39A.sqlcbli`

No source file was deleted from disk.

Backups created:

- `inventory/parser_lab_inventory.before-delete-pindpis39a-20260821.sqlite`
- `inventory/parser_lab_inventory.before-cementera-clean-refresh-20260821.sqlite`
