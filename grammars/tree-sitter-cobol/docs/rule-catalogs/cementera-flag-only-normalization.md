# Cementera Flag-Only Normalization

## Purpose

Remove residual FastParse `hasErrors=true` flags in Cementera SQL_COBOL files where Tree-sitter exposed no visible `ERROR` nodes, no `MISSING` nodes, and zero error bytes.

## Included Forms

The normalization is applied only to parser input views, not to original COBOL files.

Supported local malformed forms:

- `PROCEDURE DIVISION` with omitted period before procedure statements.
- `PROCEDURE DIVISION USINGL.` as a compact legacy typo, normalized to `PROCEDURE DIVISION USING L.`.
- `MOVE ... TO .` or fixed-layout-trimmed `MOVE ... TO` when the next code line has already started a new statement or paragraph.
- `PERFORM <label> THRU <label>` without a period immediately before the next paragraph header.

## Excluded Forms

- Valid continued `MOVE ... TO` statements where the destination appears on the next continuation line.
- General semantic repair of invalid COBOL.
- Source rewriting. The source bytes in the inventory remain unchanged.

## Cementera Files Fixed

| File | Pattern |
| --- | --- |
| `PACCOUNT01.sqlcbli` | `PROCEDURE DIVISION` without period before `PERFORM` |
| `PPREV570VF.sqlcbli` | `PROCEDURE DIVISION USINGL.` compact typo |
| `PNFEDILA05.sqlcbli` | second inline `MOVE ... TO` missing destination |
| `PQUESTDP12.sqlcbli` | `MOVE ... TO .` missing destination |
| `PNOTAGEN.sqlcbli` | `PERFORM ... THRU ...` missing period before next paragraph |
| `PNOTAPED01.sqlcbli` | `PERFORM ... THRU ...` missing period before next paragraph |

## Audit Result

Final Cementera run:

- Files: 4,169
- Parsed OK: 4,169
- Hard failures: 0
- Files with ERROR: 0
- ERROR nodes: 0
- Files with MISSING: 0
- MISSING nodes: 0

Validation DB:

`runs/candidate_compare_current_cementera_zero_error_missing_flags_20260821.sqlite`
