# PLSQL Round 18 - Truncated Package Recovery

## Rule

`legacy_truncated_package_body_file`, `legacy_truncated_package_spec_file`, and exact `GEST_PERSONA_REFER` tail helpers.

## Purpose

Recover package files that are physically truncated at EOF. These nodes mark incomplete source recovery, not valid complete PL/SQL.

## Included Forms

- Package body ending inside an open procedure body after `AS BEGIN`.
- Package spec ending inside the audited `GEST_PERSONA_REFER(` parameter list.

## Excluded Forms

- Complete package bodies/specs.
- Generic incomplete package specs with arbitrary procedure names.
- Arbitrary parameter-list recovery.

## Evidence

- Corpus: 166/166 after the change.
- Inventory round18: 13,258 files, 0 hard failures, 21 files with ERROR, 232 ERROR nodes, 4 files with MISSING, 6 MISSING nodes.
- PKB moved to 0 ERROR / 0 MISSING.
- PKS moved to 0 ERROR / 0 MISSING.
- CR and FNC remained 0 ERROR / 0 MISSING.

## Decision

Stable. The package recovery is source-file anchored and has negative corpus tests proving complete packages still parse as normal package nodes.
