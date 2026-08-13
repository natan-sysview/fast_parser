# Rule Catalog: Embedded EXEC Period Separator

Status: proposed repair in experimental grammar.

## Goal

Preserve the period after embedded `EXEC SQL ... END-EXEC.` and `EXEC CICS ... END-EXEC.` blocks as a COBOL sentence or paragraph separator in PROCEDURE DIVISION.

The previous rule allowed each embedded EXEC statement to consume the trailing period. That worked for a single block, but it could hide the separator needed before the next paragraph header. In real CICS and DB2 programs, this caused broad `ERROR` recovery starting at the following paragraph.

## Intended Nodes

- `exec_cics_statement`
- `exec_sql_statement`
- `period`
- `paragraph_header`

## Accepted Forms

```cobol
     100-FIRST.
         EXEC CICS RECEIVE
              MAP('MAPA')
              RESP(WS-RESP)
         END-EXEC.
     200-NEXT.
         MOVE 'X' TO WS-FLAG.
```

```cobol
     100-FIRST.
         EXEC SQL
           INSERT INTO TABLA
           VALUES (:WS-CAMPO)
         END-EXEC.
     200-NEXT.
         GOBACK.
```

```cobol
     WORKING-STORAGE SECTION.
         EXEC SQL INCLUDE SQLCA END-EXEC.
     01 WS-FLAG PIC X.
```

## Excluded Forms

- Full CICS command grammar.
- Full DB2 SQL grammar.
- Treating arbitrary embedded text as COBOL statements.
- Promotion to `grammars/` before full inventory validation.

## Local Syntactic Shape

In PROCEDURE DIVISION, the embedded EXEC statement ends at `END-EXEC`. If a source period follows, the procedure grammar sees it as `period`, allowing the next `paragraph_header` or `section_header` to synchronize normally.

In DATA DIVISION, `EXEC SQL INCLUDE ... END-EXEC.` remains accepted by `_data_division_entry`, where the trailing period is a local data-entry terminator.

## Corpus Examples

- `exec cics period before next paragraph`
- `exec sql period before next paragraph`

## Audit Basis

The 2026-06-29 current profile issue audit found 2,750 sampled dirty files with 4,945 `ERROR` nodes. Many high-byte errors in `IBM_ZOS_CICS_DB2` started at a paragraph after a prior `END-EXEC.`, for example `ZM2OLD59`, `SOMPO04P`, `MA2C8330`, and `UH2CVJH0`.

## Success Criteria

- `tree-sitter generate` succeeds.
- `tree-sitter test` passes with existing EXEC SQL/CICS examples and the new paragraph-separator regressions.
- Real smoke files with repeated embedded EXEC blocks reduce broad `ERROR` spans.
- Full FastParse inventory validation has zero hard failures.
- `ERROR` and `MISSING` totals do not regress unexplained.

## Validation Result

Validated on 2026-06-29 against the COBOL inventory of 74,151 non-JCL files.

- `tree-sitter generate`: passed.
- `tree-sitter test`: 132/132 passed.
- FastParse extension build target `fastparse_language_cobol`: passed.
- Parsed OK: 74,151.
- Hard failures: 0.
- Parser error-flag files: 31,929 before, 12,689 after.
- Strict `ERROR` files: 31,928 before, 12,684 after.
- `ERROR` nodes: 34,397 before, 14,381 after.
- Files with `MISSING`: 1 before, 1 after.
- `MISSING` nodes: 1 before, 1 after.
- Files became strict-ERROR clean: 19,244.
- Clean files that became strict-ERROR dirty: 0.
- Files with increased `MISSING`: 0.

Decision: stable experimental repair. Keep in `experimental-grammars/tree-sitter-cobol` only.

Artifacts:

- Report: `runs/cobol_embedded_exec_period_separator_repair_report.md`.
- Validation DB: `runs/candidate_compare_current_embedded_exec_period_separator_full.sqlite`.
- Repair audit: `audits/embedded_exec_period_separator_repair/`.
- Profile report: `runs/cobol_embedded_exec_period_separator_profile_validation_summary_report.md`.
