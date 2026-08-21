# Carlos + Cementera FastParse Retest - 2026-08-21

## Scope

FastParse validation with the current COBOL language extension:

`/Users/natanbarronlugo/Desktop/Proyectos/javaswing/assessment_csharp/native/tree-sitter-multi-parser-lab/bin/libfastparse_language_cobol.dylib`

Layout normalization:

`normal-fixed`

## Carlos

Source root:

`/Users/natanbarronlugo/Desktop/Proyectos/componentes/cobol_moderniza_carlos`

Run DB:

`runs/candidate_compare_current_carlos_fastparse_retest_20260821.sqlite`

| Metric | Count |
| --- | ---: |
| Files | 91 |
| Parsed OK | 91 |
| Hard failures | 0 |
| Files with ERROR | 0 |
| ERROR nodes | 0 |
| Files with MISSING | 0 |
| MISSING nodes | 0 |
| Strict problem rows | 0 |

By subtype:

| Subtype | Files | Files with ERROR | ERROR nodes | Files with MISSING | MISSING nodes |
| --- | ---: | ---: | ---: | ---: | ---: |
| COPYBOOK | 38 | 0 | 0 | 0 | 0 |
| PROGRAM | 51 | 0 | 0 | 0 | 0 |
| SQL_COBOL | 2 | 0 | 0 | 0 | 0 |

Elapsed: 0.645s.

## Cementera

Source root:

`/Users/natanbarronlugo/Desktop/Proyectos/componentes/coboles/cementera`

Run DB:

`runs/candidate_compare_current_cementera_fastparse_retest_20260821.sqlite`

| Metric | Count |
| --- | ---: |
| Files | 4,169 |
| Parsed OK | 4,169 |
| Hard failures | 0 |
| Files with ERROR | 0 |
| ERROR nodes | 0 |
| Files with MISSING | 0 |
| MISSING nodes | 0 |
| Strict problem rows | 0 |

By subtype:

| Subtype | Files | Files with ERROR | ERROR nodes | Files with MISSING | MISSING nodes |
| --- | ---: | ---: | ---: | ---: | ---: |
| COPYBOOK | 149 | 0 | 0 | 0 | 0 |
| PROGRAM | 454 | 0 | 0 | 0 | 0 |
| SQL_COBOL | 3,566 | 0 | 0 | 0 | 0 |

Elapsed: 26.972s.

## Decision

Both source roots validate cleanly with FastParse: no hard failures, no `hasErrors`, no `ERROR` nodes, and no `MISSING` nodes.
