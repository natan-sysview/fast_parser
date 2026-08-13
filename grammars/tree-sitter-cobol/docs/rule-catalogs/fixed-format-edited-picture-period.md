# Rule Catalog: Fixed-Format Edited Picture Period

Status: implemented in experimental grammar.

## Goal

Parse fixed-format data descriptions where an edited `PIC` string contains punctuation, ends at zero-based column 70, and the statement period is in zero-based column 71.

Observed inventory shape:

```cobol
021600    05 WA-CIFRA1                      PIC -ZZZ,ZZZ,ZZZ,ZZZ,ZZ9.99.02060069
```

The decimal point inside `ZZ9.99` is part of the picture. The final period at the fixed source boundary terminates the data-description entry. The trailing digits belong to the sequence/identification area.

## Included Forms

- Edited picture masks with punctuation such as comma, sign, slash, currency/edit characters, and internal decimal points.
- Candidates where the final picture character is in zero-based column 70 and the following period is in zero-based column 71.
- Data-description `picture_clause` only.

## Excluded Forms

- Ordinary edited pictures whose terminating period is not in fixed-format column 71.
- Global changes to `picture_edit`.
- Semantic validation of edited picture masks.
- Full fixed-format source conversion.

## Implementation Shape

Add a hidden external `_fixed_format_picture_edit` token under the existing named `picture_edit` rule. The external scanner consumes picture-edit characters only up to zero-based column 70 and accepts the token only when the next character is the fixed-format statement period at zero-based column 71.

## Corpus Coverage

- Positive: `PIC -ZZZ,ZZZ,ZZZ,ZZZ,ZZ9.99.` before sequence digits.
- Negative: ordinary `PIC -ZZZ,ZZ9.99.` remains a regular `picture_edit`.

## Validation Plan

- Generate parser.
- Run focused corpus and full corpus.
- Smoke parse `SA3CA501` and `SA3CD421`, which showed new `MISSING "."` nodes in the exploratory `DATA-BASE SECTION` candidate.
- Rebuild FastParse COBOL language extension.
- Run full inventory validation against `runs/candidate_compare_current_fixed_format_unsigned_numeric_value_period_full.sqlite`.
- Accept only if `MISSING` returns to baseline or improves and no new `ERROR` regressions appear.

## Validation Result

Validated as part of the combined `DATA-BASE SECTION` plus fixed-format edited
picture batch on 2026-06-29.

- Corpus: 156/156 passed.
- Focused corpus: 2/2 `fixed_format_edited_picture_period` cases passed.
- Smoke parse: `SA3CA501` and `SA3CD421` changed from `MISSING "."` in the exploratory candidate to clean parses.
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
- Missing-node regressions: 0.

Text audit:

- Fixed-format edited `PIC` hits: 1,031 lines in 400 files.
- Hits in files with lower `ERROR` counts: 396.
- Hits in files that became clean: 352.

## Artifacts

- Baseline before: `baselines/2026-06-29-before-fixed-format-edited-picture-period-repair`.
- Final validation DB: `runs/candidate_compare_current_database_section_fixed_format_edited_picture_full.sqlite`.
- Final report: `runs/cobol_database_section_fixed_format_edited_picture_repair_report.md`.
- Final audit: `audits/database_section_fixed_format_edited_picture_repair/`.
