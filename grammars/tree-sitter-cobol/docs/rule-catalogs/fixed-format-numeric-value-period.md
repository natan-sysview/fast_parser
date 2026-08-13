# Rule Catalog: Fixed-Format Numeric Value Period

Status: implemented in experimental grammar.

## Goal

Parse fixed-format data-description values where an integer `VALUE` item ends at column 71 and the terminating period is at column 72, immediately followed by sequence digits.

Observed inventory shape:

```cobol
013700   05 WC-LEIDOS                         PIC S9(07) COMP-3 VALUE 0.00013700
054300     05  CON-C-SELECT                PIC S9(3)  COMP-3 VALUE +440.05430000
```

The COBOL source area ends at the period after the integer value. The trailing digits belong to the sequence/identification area, but the normal decimal token can read the whole text as one decimal literal.

## Included Forms

- The original one-digit data-description `VALUE 0.` form where the digit is in zero-based column 70 and the period is in zero-based column 71.
- Signed integer `VALUE` items beginning near the right side of the source area, with optional `+` or `-`, when the signed integer reaches the fixed-format period shape.
- Unsigned multi-digit integer `VALUE` items beginning near the right side of the source area, only when the integer reaches zero-based column 70 and the following period is in zero-based column 71.
- Optional sequence or identification text after the fixed-format period.

## Excluded Forms

- Real decimal literals such as `VALUE 0.25.`.
- Real signed decimal literals such as `VALUE +0.25.`.
- Unsigned multi-digit values where the decimal point is not the fixed-format period in zero-based column 71.
- Fixed-format values with an actual fractional component before the source-area period.
- Full fixed-format source conversion.
- Global changes to decimal literal precedence.

## Implementation Shape

The scanner exposes a hidden `_fixed_format_integer_value` when it sees either:

- The original proven one-digit case: a digit in zero-based column 70.
- A signed integer that starts near the right side of the source area and is used as a `VALUE` item.
- An unsigned multi-digit integer that starts near the right side of the source area, consumes only digits through zero-based column 70, and stops before the fixed-format period in zero-based column 71.

The grammar accepts that token only in `value_item` and aliases it as `integer`.

The existing `_fixed_format_period` then consumes the period in zero-based column 71 as the data-description terminator.

An earlier variant placed `_fixed_format_integer_value` inside the global `number` rule. Full inventory validation showed that this also affected procedure expressions near column 72, for example `UNTIL I > 20`, and created 24 newly dirty files. That variant was rejected. The kept implementation is scoped to data-description `VALUE` items.

## Corpus Coverage

- Positive: `VALUE 0.` before fixed-format suffix digits.
- Positive: `VALUE +440.` before fixed-format suffix digits.
- Positive: negative `VALUE -12.` before fixed-format suffix digits.
- Positive: unsigned multi-digit `VALUE 999.` before fixed-format suffix digits.
- Negative: ordinary decimal `VALUE 0.25.` remains a `decimal`.
- Negative: ordinary signed decimal `VALUE +0.25.` remains a `decimal`.
- Negative: ordinary unsigned decimal `VALUE 999.12.` remains a `decimal`.

## Validation Plan

- Generate parser.
- Run focused corpus and full corpus.
- Rebuild the FastParse COBOL language extension.
- Run full inventory validation against the previous stable v2 DB.
- Audit changed files, with special attention to ordinary decimals and files that become newly dirty.

## Validation Result

### Unsigned multi-digit extension, 2026-06-29

Validated against the full COBOL inventory after the DATE FORMAT clause
baseline.

- Corpus: 151/151 passed.
- Inventory files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- Parser error-flag files: 10,656 before, 10,556 after.
- Strict files with `ERROR`: 10,651 before, 10,551 after.
- `ERROR` nodes: 11,711 before, 11,585 after.
- Files with `MISSING`: 1 before, 1 after.
- `MISSING` nodes: 1 before, 1 after.
- Files became clean by parser error flag: 100.
- Files became newly dirty by parser error flag: 0.
- Files with lower `ERROR` count: 106.
- Files with higher `ERROR` count: 0.
- Full validation throughput: 252.5 files/sec with diagnostics persisted.

Text audit:

- Fixed unsigned integer `VALUE`/`VALUES` period hits: 5,073 lines in 721 files.
- Hits in files with lower `ERROR` counts: 512.
- Hits in files that became clean: 493.
- Hits in files that became dirty: 0.

The implementation keeps the token scoped to data-description `value_item`,
requires digits to end at zero-based column 70, and requires the following
period to be in zero-based column 71. Ordinary decimals remain covered by
negative corpus examples, including a right-side `VALUE 999.12.` case.

### Signed-only extension, 2026-06-29

Validated against the full COBOL inventory after the abbreviated comparison
continuation baseline.

- Corpus: 137/137 passed.
- Inventory files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- Parser error-flag files: 11,137 before, 10,899 after.
- Strict files with `ERROR`: 11,132 before, 10,894 after.
- `ERROR` nodes: 12,645 before, 12,051 after.
- Files with `MISSING`: 1 before, 1 after.
- `MISSING` nodes: 1 before, 1 after.
- Files became clean by parser error flag: 238.
- Files became newly dirty by parser error flag: 0.
- Files with lower `ERROR` count: 286.
- Files with higher `ERROR` count: 0.
- Full validation throughput: 1,161.3 files/sec.

Rejected variant:

- A broader signed-and-unsigned multi-digit scanner variant reduced parser
  error-flag files to 10,776, but increased `ERROR` nodes from 12,645 to
  40,772 and regressed 238 files. It was rejected and kept only as audit
  evidence.

### One-digit value period repair, 2026-06-26

Validated on 2026-06-26 against the full COBOL inventory.

- Corpus: 109/109 passed.
- Inventory files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- Strict files with `ERROR`: 34,303 before, 34,185 after.
- `ERROR` nodes: 38,744 before, 37,545 after.
- Files with `MISSING`: 18 before, 18 after.
- `MISSING` nodes: 18 before, 18 after.
- Files became clean by strict `ERROR`: 118.
- Files became newly dirty by strict `ERROR`: 0.
- Files with lower `ERROR` count: 255.
- Files with higher `ERROR` count: 1.

Known residual:

- `MF4CM030` was already dirty due to an unresolved `EXEC SQL DECLARE CURSOR` recovery span and changed from 1 to 2 `ERROR` nodes. It is documented as an existing-dirty recovery tradeoff, not a newly dirty file.

## Artifacts

- Baseline before: `baselines/2026-06-26-before-fixed-format-numeric-value-period-v2-repair`.
- Validation DB: `runs/candidate_compare_current_fixed_format_numeric_value_period_value_item_scoped_full.sqlite`.
- Profile report: `runs/cobol_fixed_format_numeric_value_period_value_item_scoped_profile_validation_summary_report.md`.
- Signed-only baseline before: `baselines/2026-06-29-before-fixed-format-signed-numeric-value-period-repair`.
- Signed-only validation DB: `runs/candidate_compare_current_fixed_format_signed_numeric_value_period_signed_only_full.sqlite`.
- Signed-only profile report: `runs/cobol_fixed_format_signed_numeric_value_period_signed_only_profile_validation_summary_report.md`.
- Signed-only audit CSVs: `audits/fixed_format_signed_numeric_value_period_signed_only_repair/`.
- Unsigned extension baseline before: `baselines/2026-06-29-before-fixed-format-unsigned-numeric-value-period-repair`.
- Unsigned extension validation DB: `runs/candidate_compare_current_fixed_format_unsigned_numeric_value_period_full.sqlite`.
- Unsigned extension report: `runs/cobol_fixed_format_unsigned_numeric_value_period_repair_report.md`.
- Unsigned extension audit CSVs: `audits/fixed_format_unsigned_numeric_value_period_repair/`.
