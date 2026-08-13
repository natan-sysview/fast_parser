# FD COPY Record Descriptions

## Rule Name

`file_description`

## Purpose

Allow `FD` and `SD` file descriptions to omit inline record descriptions when the record layout is supplied by a following `COPY` statement.

## Basis

The current COBOL issue-node audit found `FILE_CONTROL_IO` as the dominant residual family in the targeted profile sample. Real samples show file descriptions such as:

- `FD FD-REMSENT ... DATA RECORD IS REMSENT-REC. COPY SOMPB10C.`
- `FD EUVSM000. COPY EUVSM000.`
- `FD ARCH-A1-PROD. COPY SYWCVSAM.`

## Included Forms

- `FD name.`
- `FD name ... DATA RECORD IS record-name.`
- `SD name.`
- A following `COPY` statement handled by the existing `copy_statement` extra.

## Excluded Forms

- Expansion of copybook contents.
- Validation that the copied member actually defines the record layout.
- Unsupported file-description clauses such as Tandem `VALUE PROTECTION` and `VALUE SECURITYTYPE`; those remain separate repair candidates.

## Local Syntax Supported

`file_description` now accepts an optional `record_description_list` after `file_description_entry`. Existing inline `01`/`05` record descriptions remain attached to the `file_description` when present.

## Known Limits

The grammar recognizes only local syntax. It does not link `DATA RECORD IS name` to the copied copybook or verify copybook availability.

## Audit Result Summary

Validation date: 2026-06-26.

- Corpus: 105/105 passed.
- Full COBOL inventory: 74,151 files parsed OK.
- Hard failures: 0.
- Files with `ERROR`: 44,458 -> 42,276.
- `ERROR` nodes: 51,019 -> 46,672.
- Files with `MISSING`: 17 -> 17.
- `MISSING` nodes: 17 -> 17.
- Became clean: 2,182 files.
- Became dirty: 0 files.
- Existing dirty files with higher `ERROR` node count: 16; each increased by one node, with no newly dirty file and lower aggregate error bytes.

Primary improvement landed in IBM z/OS DB2 SQL COBOL and IBM z/OS batch program profiles, matching the sampled `FD ... COPY ...` pattern.
