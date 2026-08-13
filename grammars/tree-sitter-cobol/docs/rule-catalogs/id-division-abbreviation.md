# Rule Catalog: ID DIVISION Abbreviation

Status: implemented in experimental grammar.

## Goal

Recognize the COBOL abbreviation `ID DIVISION.` as an equivalent header form for `IDENTIFICATION DIVISION.`.

Residual audit examples include:

```cobol
ID DIVISION.
```

```cobol
ID                      DIVISION.
```

## Included Forms

- `ID DIVISION.`.
- Mixed-case spelling through the existing case-insensitive keyword style.
- Variable whitespace between `ID` and `DIVISION`.

## Excluded Forms

- Changes to `PROGRAM-ID`.
- Other division abbreviations not observed or confirmed in this repair.
- Semantic validation of identification metadata.
- Recovery around comments or decorative headers that merely mention "identification division" inside comments.

## Implementation Shape

Extend hidden `_IDENTIFICATION` to accept either the full `IDENTIFICATION` keyword or the `ID` abbreviation. The change remains scoped to `identification_division`, because `_IDENTIFICATION` is only expected where a division header is parsed.

## Corpus Coverage

- Minimal program using `ID DIVISION.`.
- Minimal program using spaced `ID                      DIVISION.`.

## Validation Plan

- Generate parser.
- Run `tree-sitter test`.
- Rebuild FastParse COBOL extension.
- Run full inventory validation.
- Compare against `runs/candidate_compare_current_exec_sql_db2_negated_operators_full.sqlite`.
- Audit newly dirty files before deciding.

## Validation Result

Validated on 2026-06-26 against the full COBOL inventory.

- Corpus: 116/116 passed.
- Inventory files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- Strict files with `ERROR`: 33,777 before, 33,092 after.
- `ERROR` nodes: 36,571 before, 35,918 after.
- Files with `MISSING`: 18 before, 18 after.
- `MISSING` nodes: 18 before, 18 after.
- Files became clean by strict `ERROR`: 685.
- Files became newly dirty by strict `ERROR`: 0.
- Files with lower `ERROR` count: 685.
- Files with higher `ERROR` count: 11.
- Net error-byte reduction: 50,579,640 bytes.

Known residual:

- Eleven already-dirty files increased in `ERROR` node count after the parser recovered past the `ID DIVISION.` header. No file became newly dirty.

## Artifacts

- Baseline before: `baselines/2026-06-26-before-id-division-abbreviation-repair`.
- Validation DB: `runs/candidate_compare_current_id_division_abbreviation_full.sqlite`.
- Profile report: `runs/cobol_id_division_abbreviation_profile_validation_summary_report.md`.
- Audit CSVs: `audits/id_division_abbreviation_repair/`.

Decision: kept as stable experimental repair with documented existing-dirty recovery tradeoffs.
