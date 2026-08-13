# Rule Catalog: Recording Mode Variants

Status: implemented in experimental grammar.

## Rule Name

`recording_mode_clause`

## Purpose

Recognize the observed `RECORDING MODE ARE <mode>` file-description variant
without broadening unrelated `FD` syntax.

## Basis

The current post-EJECT validation baseline still has 31,933 strict `ERROR`
files and 34,436 `ERROR` nodes. A targeted source scan across the 74,151
non-JCL COBOL inventory files found:

- `RECORDING MODE ARE ...`: 39 matches in 14 files.
- All 14 files currently have parse errors.
- Inventory profiles: `IBM_ZOS_DB2` 10 files, `IBM_ZOS_BATCH` 2 files,
  `IBM_ZOS_CICS_DB2` 2 files.
- Inventory subtypes: `SQL_COBOL` 10 files, `PROGRAM` 4 files.

## Included Forms

```cobol
       FD  FD-INPUT
           LABEL RECORD ARE STANDARD
           RECORDING MODE ARE F.
```

Existing accepted forms remain supported:

```cobol
       FD  FD-OUTPUT
           RECORDING MODE IS F.
```

```cobol
       FD  FD-OUTPUT
           RECORDING MODE F.
```

## Excluded Forms

- `ACTUAL KEY` in `SELECT` clauses. A smoke A/B showed it can fragment large
  legacy `OBJECT` files into many more `ERROR` nodes until surrounding OBJECT
  syntax is improved.
- Tandem/NonStop-like `VALUE PROTECTION` and `VALUE SECURITYTYPE` file
  attributes. They reduced error-byte coverage in smoke tests, but increased
  `ERROR` node counts in large OBJECT programs, so they are deferred.
- Semantic validation of whether `ARE` is preferred for singular/plural
  agreement.

## Grammar Shape

`recording_mode_clause` now accepts optional `IS` or `ARE` before the existing
mode word:

```text
RECORDING [MODE] [IS|ARE] WORD
```

The public tree shape remains stable: the clause still exposes
`recording_mode_clause` with `mode: (WORD)`.

## Corpus Coverage

- `RECORDING MODE ARE F` after `LABEL RECORD ARE STANDARD`.
- Regression coverage for `RECORDING MODE IS F`.

## Validation Plan

- Preserve a before baseline.
- Generate parser artifacts.
- Run `tree-sitter test`.
- Rebuild the FastParse COBOL language extension.
- Validate the full COBOL inventory against
  `runs/candidate_compare_current_eject_directive_full.sqlite`.
- Compare strict `ERROR` and `MISSING` metrics.
- Update this catalog with final validation metrics and audit artifacts.

## Validation Result

Validated on 2026-06-29 against 74,151 COBOL inventory files.

- `tree-sitter generate`: passed with the pre-existing ABI 14 warning because
  this grammar does not yet have `tree-sitter.json`.
- `tree-sitter test`: 130/130 passed.
- FastParse native extension: rebuilt successfully.
- Parsed OK: 74,151.
- Hard failures: 0.
- Parser error-flag files: 31,934 -> 31,929.
- Strict `ERROR` files: 31,933 -> 31,928.
- `ERROR` nodes: 34,436 -> 34,397.
- Files with `MISSING`: 1 -> 1.
- `MISSING` nodes: 1 -> 1.
- Files became strict-ERROR clean: 5.
- Clean files that became dirty: 0.
- Changed files: 14, exactly the files with `RECORDING MODE ARE`.
- Changed occurrences: 39.
- Regressed files by `ERROR` or `MISSING` count: 0.
- Validation throughput: 1,268.5 files/sec.

Artifacts:

- Report: `runs/cobol_recording_mode_variants_repair_report.md`
- Validation DB:
  `runs/candidate_compare_current_recording_mode_variants_full.sqlite`
- Rule audit: `audits/recording_mode_variants_repair/`
- Profile audit: `audits/profile_validation_current_recording_mode_variants/`
