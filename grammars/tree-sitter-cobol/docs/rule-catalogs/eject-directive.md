# Rule Catalog: EJECT Directive

Status: implemented in the experimental grammar.

## Goal

Accept fixed-format COBOL `EJECT` listing directives as compiler directives
rather than forcing them into procedure, data, or division syntax.

`EJECT` appears as a standalone source line in many inventory files and is used
to control compiler/listing pagination. It should not be treated as a COBOL
statement or data item.

## Intended Node

- `compiler_directive`

## Accepted Forms

```cobol
       EJECT
```

```cobol
050900 EJECT                                                        04520010
```

The accepted shape is a full-line fixed-format directive:

- optional six-column sequence area made of spaces/digits,
- optional spaces,
- `EJECT` case-insensitively,
- optional spaces/digits to line end.

## Excluded Forms

- `EJECT` used as an identifier or operand.
- `EJECT` embedded inside a statement, for example `MOVE EJECT TO WS-A`.
- JCL/index files that merely contain `EJECT` outside the COBOL inventory.
- Other plain-word listing directives such as `SKIP1`, `SKIP2`, `SKIP3`,
  `TITLE`, or `SPACE`, until separately audited.

## Pre-Change Inventory Audit

Baseline: `runs/candidate_compare_current_value_literal_case_variants_v2_full.sqlite`.

- Fixed-format `EJECT` lines: 27,947 matches.
- Files with `EJECT`: 2,076.
- Dirty files with `EJECT`: 2,008.
- Strict ERROR files with `EJECT`: 2,001.
- Missing-node files with `EJECT`: 16.

## Corpus Examples

- `test/corpus/eject_directive.txt`: `EJECT` between COBOL divisions/sections.
- `test/corpus/eject_directive.txt`: `MOVE EJECT TO WS-A` remains an operand,
  not a compiler directive.

## Validation Plan

- Generate parser artifacts.
- Run full corpus.
- Build the FastParse COBOL extension.
- Validate the full COBOL inventory.
- Compare against the value-literal-case-variants v2 baseline.
- Audit targeted `EJECT` files and update this catalog with final metrics.

## Validation Result

Validated on 2026-06-26 against the COBOL inventory.

- `tree-sitter generate`: passed.
- `tree-sitter test`: 128/128 passed.
- FastParse native build: passed.
- Inventory files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- Strict ERROR files: 32,634 before, 31,933 after.
- ERROR nodes: 35,508 before, 34,436 after.
- MISSING nodes: 18 before, 1 after.
- Strict files became clean: 701.
- Clean files became dirty: 0.
- Improved files by diagnostics: 1,964.
- Regressed dirty files by at least one local metric: 72.

No clean file became dirty. The regressed set consists of files that already
had parse errors; most have lower error-byte span after recovery moves past
`EJECT` lines, but some split one broad error into multiple smaller errors.

## Artifacts

- Report: `runs/cobol_eject_directive_repair_report.md`.
- Full validation DB: `runs/candidate_compare_current_eject_directive_full.sqlite`.
- Profile report: `runs/cobol_eject_directive_profile_validation_summary_report.md`.
- Repair audit: `audits/eject_directive_repair/`.
- Profile audit: `audits/profile_validation_current_eject_directive/`.
