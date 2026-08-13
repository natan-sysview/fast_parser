# Linkage Section Copy-Only Body

## Rule Name

`linkage_section`

## Purpose

Accept `LINKAGE SECTION` blocks whose only source content is one or more
copybook statements.

## Basis

The current issue-node audit showed many residual errors at `LINKAGE SECTION`
headers in programs where the section body is supplied entirely by `COPY`
statements. Example shape:

- `LINKAGE SECTION.`
- `COPY AXWCPS13.`
- `PROCEDURE DIVISION USING PS13-REG.`

## Local Syntax Supported

`linkage_section` now uses `repeat($._data_division_entry)` instead of
`repeat1($._data_division_entry)`, matching the tolerance already used by
`working_storage_section`.

`COPY` remains a global `copy_statement` extra in this grammar. This repair does
not change copybook expansion or make `COPY` a semantic data item.

## Known Limits

- Copybooks are not expanded.
- `COPY` is still represented as a `copy_statement` extra rather than a true
  `linkage_section` child in this rule.
- Empty `LINKAGE SECTION.` is accepted syntactically; semantic validation is out
  of scope for the parser.

## Corpus Examples Covered

- `LINKAGE SECTION.` followed only by `COPY AXWCPS13.` before `PROCEDURE DIVISION`.

## Audit Result Summary

Validation date: 2026-06-30.

- Corpus: 163/163 passed.
- Full COBOL inventory: 74,151 files parsed OK.
- Hard failures: 0.
- Files with `ERROR`: 10,401 -> 3,455.
- `ERROR` nodes: 11,325 -> 4,090.
- Files with `MISSING`: 1 -> 1.
- `MISSING` nodes: 1 -> 1.
- Became clean: 6,946 files.
- Became dirty: 0 files.
- Error-node regressions: 0 files.

Primary improvement landed in IBM z/OS DB2, IBM z/OS batch, and IBM z/OS DB2
program profiles, with no aggregate regression in Tandem, Micro Focus, CICS, or
copybook slices.
