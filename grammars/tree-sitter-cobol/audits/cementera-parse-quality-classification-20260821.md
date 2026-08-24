# Cementera Parse Quality Classification - 2026-08-21

Inventory DB:
`/Users/natanbarronlugo/Desktop/Proyectos/javaswing/assessment_csharp/native/tree-sitter-multi-parser-lab/inventory/parser_lab_inventory.sqlite`

Validation report:
`/Users/natanbarronlugo/Desktop/Proyectos/fast_parser/grammars/tree-sitter-cobol/runs/cementera-wide-4169-current-20260821.json`

Parser flow:
`ParseBytes + Diagnostics + AutoSafe`

Classification run:
`cobol_parse_quality_runs.id = 1`

Current view:
`v_cobol_current_parse_quality`

## Summary

| quality_class | files | hasErrors | ERROR | MISSING | grammar_score_target |
|---|---:|---:|---:|---:|---:|
| GRAMMAR_TARGET | 4137 | 0 | 0 | 0 | 4137 |
| SOURCE_CORRUPT | 15 | 15 | 15 | 0 | 0 |
| REPARABLE_GRAMMAR | 5 | 5 | 4 | 1 | 5 |
| NON_COBOL_EMBEDDED | 4 | 4 | 4 | 0 | 0 |
| REPARABLE_NORMALIZER | 4 | 4 | 4 | 0 | 4 |
| DIAGNOSTIC_FLAG_ONLY | 3 | 3 | 0 | 0 | 0 |
| FRAGMENT_COBOL | 1 | 1 | 1 | 0 | 1 |

## Notes

- `GRAMMAR_TARGET` files are clean in the current full Cementera validation and should stay in the grammar score.
- `REPARABLE_GRAMMAR`, `REPARABLE_NORMALIZER`, and `FRAGMENT_COBOL` are valid targets for future grammar/AutoSafe work.
- `SOURCE_CORRUPT` and `NON_COBOL_EMBEDDED` are preserved in inventory but should not be counted as grammar failures unless manually reclassified.
- `DIAGNOSTIC_FLAG_ONLY` means `hasErrors=true` with `ERROR=0` and `MISSING=0`; these need separate FastParse diagnostics investigation.

Useful query:

```sql
SELECT quality_class, quality_reason, name, absolute_path
FROM v_cobol_current_parse_quality
WHERE quality_class <> 'GRAMMAR_TARGET'
ORDER BY quality_class, name;
```
