# Cementera Reparable Cases - 2026-08-21

## Scope

FastParse local build with COBOL language extension, `ParseBytes`, diagnostics output, and `auto_safe` normalization.

Focused set from `v_cobol_current_parse_quality`:

- `5` `REPARABLE_GRAMMAR`
- `4` `REPARABLE_NORMALIZER`
- `1` `FRAGMENT_COBOL`

## Result

The focused set is clean after the grammar and normalizer changes:

| Files | hasErrors | ERROR | MISSING |
| ---: | ---: | ---: | ---: |
| 10 | 0 | 0 | 0 |

Per-file verification:

| File | Class | Previous | Current |
| --- | --- | --- | --- |
| `ENTRADA.cblile` | `FRAGMENT_COBOL` | `ERROR=1 MISSING=0` | `hasErrors=false ERROR=0 MISSING=0` |
| `PBAVA020.sqlcbli` | `REPARABLE_GRAMMAR` | `ERROR=1 MISSING=0` | `hasErrors=false ERROR=0 MISSING=0` |
| `PCOMP003.sqlcbli` | `REPARABLE_GRAMMAR` | `ERROR=1 MISSING=0` | `hasErrors=false ERROR=0 MISSING=0` |
| `PPALETVDA3.rqlcbli` | `REPARABLE_GRAMMAR` | `ERROR=0 MISSING=1` | `hasErrors=false ERROR=0 MISSING=0` |
| `PPALM064.sqlcbli` | `REPARABLE_GRAMMAR` | `ERROR=1 MISSING=0` | `hasErrors=false ERROR=0 MISSING=0` |
| `PRV10015.sqlcbli` | `REPARABLE_GRAMMAR` | `ERROR=1 MISSING=0` | `hasErrors=false ERROR=0 MISSING=0` |
| `CONV101.cblile` | `REPARABLE_NORMALIZER` | `ERROR=1 MISSING=0` | `hasErrors=false ERROR=0 MISSING=0` |
| `PNFEDILA05.sqlcbli` | `REPARABLE_NORMALIZER` | `ERROR=1 MISSING=0` | `hasErrors=false ERROR=0 MISSING=0` |
| `PPREV565.sqlcbli` | `REPARABLE_NORMALIZER` | `ERROR=1 MISSING=0` | `hasErrors=false ERROR=0 MISSING=0` |
| `PSTA025.sqlcbli` | `REPARABLE_NORMALIZER` | `ERROR=1 MISSING=0` | `hasErrors=false ERROR=0 MISSING=0` |

## Wider Cementera Scan

Expanded Cementera universe: files whose extension contains `cbl`, plus `.cob` and `.cpy`.

| Files | OK | Hard Fail | hasErrors | ERROR | MISSING | Lines | Workers | Seconds |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4,169 | 4,169 | 0 | 51 | 48 | 0 | 2,319,003 | 12 | 1.774 |

Remaining failures by inventory class:

| Class | grammar_score_target | Files |
| --- | ---: | ---: |
| `DIAGNOSTIC_FLAG_ONLY` | 0 | 3 |
| `NON_COBOL_EMBEDDED` | 0 | 4 |
| `SOURCE_CORRUPT` | 0 | 15 |
| `GRAMMAR_TARGET` | 1 | 29 |

## Validation

- `tree-sitter generate`
- `tree-sitter test --rebuild`: `300/300`
- `cmake --build build-normalizer-0.1.1 --config Release`
- `python3 -m unittest tests.test_tsmp_contract.TsmpContractTests.test_cobol_auto_safe_normalization_handles_fixed_layout_view_repairs`

## Notes

The focused repair set is complete. A broader normalizer attempt for `COMPUTE (...).` and historical `*n` comment lines was tested, but it increased the expanded Cementera failures from `51` to `94`; that attempt was reverted. The remaining `29` `GRAMMAR_TARGET` files should be handled as the next grammar batch with narrower corpus-backed rules.
