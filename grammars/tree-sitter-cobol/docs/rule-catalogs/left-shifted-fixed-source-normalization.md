# Left Shifted Fixed Source Normalization

## Rule name

`left_shifted_fixed_source_to_area_a`

## Purpose

Normalize fixed-layout COBOL files whose inventory profile says source starts at column 8, but whose division headers and `PROGRAM-ID` physically start before column 8. Without this correction the fixed-layout prefix blanking removes the first six characters of valid COBOL headers, producing damaged input such as `IFICATION DIVISION.` and `AM-ID.`.

## Included forms

- Fixed COBOL profile with indicator column 7 and source start column 8.
- One of the first 100 physical lines has a COBOL structural header before source column 8:
  - `IDENTIFICATION DIVISION`
  - `ENVIRONMENT DIVISION`
  - `DATA DIVISION`
  - `PROCEDURE DIVISION`
  - `PROGRAM-ID`

## Excluded forms

- Files whose structural headers already start at or after column 8.
- Files without early division/program headers.
- Non-fixed layout profiles.
- Non-`normal-fixed` parsing contexts.

## Local syntactic shape

The normalization prepends six spaces to nonblank physical lines before the existing fixed-layout pass. The normal fixed pass then blanks columns 1-6 and preserves the intended COBOL source text in columns 8-72.

## Evidence

Baseline:

```text
baselines/2026-08-21-before-cementera-left-shifted-fixed-normalization/cobol_layout_normalization.py
```

Validation DB:

```text
runs/candidate_compare_current_cementera_left_shifted_fixed_normalization_20260821.sqlite
```

Audit DB:

```text
audits/cementera_left_shifted_fixed_normalization_20260821/issue_nodes.sqlite
```

Scope check activated on one Cementera file:

```text
KNORRBK.cbl
```

## Result

Compared with `current_cementera_incomplete_indicator8_filler_normalization_20260821`:

- Files: `4169`
- Parsed OK: `4169`
- Hard failures: `0`
- Files with ERROR: `26 -> 25`
- ERROR nodes: `20 -> 19`
- Files with MISSING: `0 -> 0`
- MISSING nodes: `0 -> 0`
- Improved file: `KNORRBK.cbl`
- Regressions: none observed

## Known semantic limits

This rule corrects a physical-layout mismatch. It does not infer dialect or semantic intent; it only prevents fixed-column normalization from destroying COBOL headers that visibly start too far left for the recorded profile.
