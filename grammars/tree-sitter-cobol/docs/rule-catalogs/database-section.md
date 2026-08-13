# Rule Catalog: DATA-BASE SECTION

Status: implemented in experimental grammar.

## Goal

Recognize Burroughs-style `DATA-BASE SECTION` blocks inside the COBOL Data Division.

Observed inventory shape:

```cobol
003900 DATA-BASE        SECTION.
004100 DB  S264BD03SERVHISDB.
004200 01  S264B02HISMONNAC.
004300 01  S264B03HISMONEXT.
005000 WORKING-STORAGE SECTION.
```

## Included Forms

- `DATA-BASE SECTION.` inside `DATA DIVISION`.
- One or more `DB name.` entries inside the section.
- Level-number data entries after each `DB name.` line.
- Multiple `DB name.` groups before `WORKING-STORAGE SECTION`.

## Excluded Forms

- `DATABASE SECTION` text that appears only in comments.
- Semantic validation of database names or database schema membership.
- Expansion of copybooks or database metadata.
- Lines where the first source character is collapsed into the fixed-format indicator column, such as `014530DATA-BASE SECTION.`. Those require a separate fixed-format normalization decision.

## Implementation Shape

Add a named `database_section` under `data_division`, after `file_section` and before `working_storage_section`.

Add a named `database_description` for `DB name.` lines, with the database name exposed as `name: qualified_word`.

Reuse existing data-description entries for the level-number records inside the section.

## Corpus Coverage

- Positive: single `DB name.` group with level-01 records.
- Positive: multiple `DB name.` groups.
- Negative: `DATABASE SECTION` in a comment remains a comment and does not create `database_section`.

## Validation Plan

- Create baseline before editing `grammar.js`.
- Generate parser.
- Run focused corpus and full corpus.
- Smoke parse real OBJECT files such as `P340_12MTP001` and `P014_13MTP004`.
- Rebuild FastParse COBOL language extension.
- Run full inventory validation against `runs/candidate_compare_current_fixed_format_unsigned_numeric_value_period_full.sqlite`.
- Audit `database_section` and `database_description` matches, plus likely misses for collapsed fixed-format lines.

## Validation Result

Validated as part of the combined `DATA-BASE SECTION` plus fixed-format edited
picture batch on 2026-06-29.

- Corpus: 156/156 passed.
- Inventory files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- Parser error-flag files: 10,556 before, 10,401 after.
- `ERROR` nodes: 11,585 before, 11,328 after.
- Files with `MISSING`: 1 before, 1 after.
- `MISSING` nodes: 1 before, 1 after.
- Files became clean by parser error flag: 155.
- Files became newly dirty by parser error flag: 0.
- Files with lower `ERROR` count: 168.
- Files with higher `ERROR` count: 0.

Text audit:

- `DATA-BASE SECTION` text hits: 21 lines in 21 PROGRAM files.
- Collapsed fixed-format indicator variants left out of scope: 2.
- `DATA-BASE SECTION` hits in files with lower `ERROR` counts: 1.

An exploratory `DATA-BASE SECTION`-only validation reduced `ERROR` nodes but
introduced two new `MISSING "."` nodes in files without `DATA-BASE SECTION`.
Those were caused by fixed-format edited `PICTURE` masks at the source-area
boundary and were resolved by the paired
`fixed-format-edited-picture-period` repair before accepting the batch.

## Artifacts

- Baseline before `DATA-BASE SECTION`: `baselines/2026-06-29-before-database-section-repair`.
- Exploratory DB with missing regression: `runs/candidate_compare_current_database_section_full.sqlite`.
- Final validation DB: `runs/candidate_compare_current_database_section_fixed_format_edited_picture_full.sqlite`.
- Final report: `runs/cobol_database_section_fixed_format_edited_picture_repair_report.md`.
- Final audit: `audits/database_section_fixed_format_edited_picture_repair/`.
