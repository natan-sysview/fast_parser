# Rule Catalog: DFHVALUE Expression

Status: implemented in the experimental grammar; validated as a narrow,
metric-neutral CICS expression repair.

## Goal

Recognize the CICS `DFHVALUE(...)` symbolic-value form as a stable COBOL node
when it appears in local expression contexts, especially level-88 `VALUE`
clauses that previously produced parser `ERROR` nodes.

## Intended Node

- `dfhvalue_expression`

## Accepted Forms

```cobol
88 APPC-CONV-STATE-ALLOCATED VALUE DFHVALUE(ALLOCATED).
```

```cobol
IF WS-STATUS = DFHVALUE(DISABLED)
   DISPLAY 'N'
END-IF.
```

The function name is case-insensitive. The argument is currently a single
COBOL word such as `OPEN`, `ALLOCATED`, `SEND`, or `ROLLBACK`.

## Excluded Forms

- Full CICS command option grammar.
- Semantic validation of CICS symbolic values.
- Nested or multi-argument `DFHVALUE` forms.
- String, numeric, or expression arguments until found in the source universe.

## Pre-Change Inventory Audit

Baseline: `runs/candidate_compare_current_burroughs_data_description_full.sqlite`.

- `DFHVALUE(...)`: 423 matches in 92 SQL_COBOL files.
- Dirty `DFHVALUE(...)` files: 89.
- Strict ERROR `DFHVALUE(...)` files: 89.
- `VALUE DFHVALUE(...)`: 13 matches in 1 SQL_COBOL file, dirty.

## Corpus Examples

- `test/corpus/dfhvalue_expression.txt`: level-88 `VALUE DFHVALUE(...)`.
- `test/corpus/dfhvalue_expression.txt`: procedure condition
  `IF ... DFHVALUE(...)`.

## Validation Plan

- Generate parser artifacts.
- Run full corpus.
- Build the FastParse COBOL extension.
- Validate the full COBOL inventory.
- Compare against the Burroughs data-description baseline.
- Audit changed files and update this catalog with final metrics.

## Validation Result

Validated on 2026-06-26 against the COBOL inventory.

- `tree-sitter generate`: passed.
- `tree-sitter test`: 124/124 passed.
- FastParse native build: passed.
- Inventory files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- Strict ERROR files: 32,638 before, 32,638 after.
- ERROR nodes: 35,516 before, 35,516 after.
- MISSING nodes: 18 before, 18 after.
- Files became clean: 0.
- Clean files became dirty: 0.
- Improved files by byte span: 1.
- Regressed files: 0.

The only measured diagnostic improvement is in `QC1CAP62`, where the error byte
span dropped from 66,772 to 65,344 bytes after the thirteen level-88
`VALUE DFHVALUE(...)` clauses parsed as local values. The file still has one
remaining `ERROR` node, so this rule does not reduce the global error-node
count.

## Node Audit

- Text `DFHVALUE(...)`: 423 matches in 92 SQL_COBOL files.
- Text `VALUE DFHVALUE(...)`: 13 matches in 1 SQL_COBOL file.
- Parsed `dfhvalue_expression` nodes: 187 nodes in 37 files.

The remaining text matches are in contexts that are either comments, raw
`EXEC CICS` command bodies, or source regions still dominated by other parse
errors. They should be revisited as part of a broader CICS command/value
diagnostic pass, not by broadening this local rule.

## Artifacts

- Report: `runs/cobol_dfhvalue_expression_repair_report.md`.
- Full validation DB: `runs/candidate_compare_current_dfhvalue_expression_full.sqlite`.
- Profile report: `runs/cobol_dfhvalue_expression_profile_validation_summary_report.md`.
- Repair audit: `audits/dfhvalue_expression_repair/`.
- Profile audit: `audits/profile_validation_current_dfhvalue_expression/`.
