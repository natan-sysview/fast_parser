# Cementera Zero Error/Missing Flags - 2026-08-21

## Scope

Validated the Cementera COBOL source root:

`/Users/natanbarronlugo/Desktop/Proyectos/componentes/coboles/cementera`

Candidate:

`current_cementera_zero_error_missing_flags_20260821`

## Evidence

- Validation DB: `runs/candidate_compare_current_cementera_zero_error_missing_flags_20260821.sqlite`
- Before baseline: `baselines/2026-08-21-before-cementera-flag-only-cleanup`
- After baseline: `baselines/2026-08-21-after-cementera-zero-error-missing-flags`
- Rule catalog: `docs/rule-catalogs/cementera-flag-only-normalization.md`

## Final Metrics

| Metric | Count |
| --- | ---: |
| Files | 4,169 |
| Parsed OK | 4,169 |
| Hard failures | 0 |
| Files with ERROR | 0 |
| ERROR nodes | 0 |
| Files with MISSING | 0 |
| MISSING nodes | 0 |

## By Subtype

| Subtype | Files | Files with ERROR | ERROR nodes | Files with MISSING | MISSING nodes |
| --- | ---: | ---: | ---: | ---: | ---: |
| COPYBOOK | 149 | 0 | 0 | 0 | 0 |
| PROGRAM | 454 | 0 | 0 | 0 | 0 |
| SQL_COBOL | 3,566 | 0 | 0 | 0 | 0 |

## Validation Command

```sh
python3 tools/compare_candidate_diagnostics.py \
  --candidate current_cementera_zero_error_missing_flags_20260821 \
  --language-extension /Users/natanbarronlugo/Desktop/Proyectos/javaswing/assessment_csharp/native/tree-sitter-multi-parser-lab/bin/libfastparse_language_cobol.dylib \
  --inventory-db /Users/natanbarronlugo/Desktop/Proyectos/javaswing/assessment_csharp/native/tree-sitter-multi-parser-lab/inventory/parser_lab_inventory.sqlite \
  --source-root /Users/natanbarronlugo/Desktop/Proyectos/componentes/coboles/cementera \
  --out-db runs/candidate_compare_current_cementera_zero_error_missing_flags_20260821.sqlite \
  --layout-normalization normal-fixed \
  --workers 12 \
  --progress-every 1000
```

## Additional Checks

- `python3 -m py_compile tools/cobol_layout_normalization.py tools/compare_candidate_diagnostics.py`
- `tree-sitter test`: 300/300 passing.

## Decision

Stable for the Cementera source root under `normal-fixed` layout normalization.
