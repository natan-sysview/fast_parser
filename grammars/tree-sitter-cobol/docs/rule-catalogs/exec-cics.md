# Rule Catalog: EXEC CICS

Status: implemented in experimental grammar, pending follow-up on regressions before any promotion.

## Goal

Recognize embedded CICS command blocks in COBOL without fully modeling CICS semantics in the first iteration.

The immediate objective is to stop `EXEC CICS ... END-EXEC` from producing cascaded `ERROR` nodes while preserving the command name as a stable child.

## Intended Nodes

- `exec_cics_statement`
- `cics_body`
- `cics_command`

## Accepted Forms

```cobol
     EXEC CICS
        IGNORE CONDITION ERROR
     END-EXEC.
```

```cobol
     EXEC CICS
        RETURN
     END-EXEC.
```

```cobol
     EXEC CICS
        LINK PROGRAM('TC2C1800')
             COMMAREA(TCWC0200)
     END-EXEC.
```

```cobol
     EXEC CICS SYNCPOINT
     END-EXEC.
```

```cobol
     EXEC  CICS
           ENTER
           TRACEID  (0)
           FROM     (PCA-TRACE-CTL)
           RESOURCE ('TRACECTL')
     END-EXEC.
```

## Excluded From First Batch

- Full CICS command grammar.
- Semantic validation of command names, option names, or option value types.
- BMS map semantics.
- SQL blocks, which must remain `exec_sql_statement`.

## Negative Examples

These should not become `exec_cics_statement`:

```cobol
     EXEC SQL
        SELECT CAMPO INTO :WS-CAMPO FROM TABLA
     END-EXEC.
```

```cobol
     MOVE 'EXEC CICS RETURN END-EXEC' TO WS-TEXT.
```

## Baseline Metrics To Beat

After the `EXEC SQL` repair:

- Files: 74,151.
- Files with `ERROR`: 59,349.
- `ERROR` nodes: 82,580.
- Files with `MISSING`: 1,691.
- `MISSING` nodes: 1,719.
- `EXEC_CICS` family: 15,179 `ERROR` nodes.

## Success Criteria

- `tree-sitter generate` succeeds.
- Corpus examples for accepted and negative forms pass.
- Full FastParse diagnostics has zero hard failures.
- `EXEC_CICS` family drops materially.
- Any regression set is saved and inspected before promotion.

## Validation Result

Validated on 2026-06-25 against the COBOL inventory of 74,151 non-JCL files.

- Parsed OK: 74,151.
- Hard failures: 0.
- Files improved: 3,370.
- Files regressed: 1,135.
- Files became clean: 2,810.
- Files became dirty: 0.
- `ERROR` nodes: 82,580 before, 79,784 after.
- `MISSING` nodes: 1,719 before, 2,340 after.
- `EXEC_CICS` family: 15,179 before, 2,086 after.

The rule is valuable but remains experimental because `MISSING` nodes increased and the regression set must stay visible before promotion.

## Artifacts

- Report: `runs/cobol_exec_cics_repair_report.md`.
- Diagnostics DB: `runs/candidate_compare_current_exec_cics_full.sqlite`.
- Binary validation DB: `runs/cobol_fastparse_binary_validation_exec_cics_full.sqlite`.
- Regression audit: `audits/exec_cics_repair/top_regressed_files.csv`.
- Residual family audit: `audits/error_family_classification_after_exec_cics/error_family_summary.csv`.
