# Next Grammar Family Roadmap

Date: 2026-06-30

## Current Closure

`java-frameworks` is now promoted and validated as a local FastParse extension. The next work should start as a separate focused cycle rather than adding unrelated scope to this grammar.

## Inventory Snapshot

Current language families in `inventory/parser_lab_inventory.sqlite` include:

| Family | Subtypes | Files |
| --- | --- | ---: |
| Java Frameworks | `framework` | 2264 |
| Java Swing | `javaswing` | 613 |
| Java Plain | `java` | 436 |
| PLSQL | `CR`, `FNC`, `PKB`, `PKS`, `PRC` | 11021 |
| PLSQL Oracle Forms | `FNC`, `PRC` | 2237 |
| COBOL | `COPYBOOK`, `JCL`, `PROGRAM`, `SQL_COBOL` | 256011 |
| Delphi | `FORM`, `INCLUDE`, `PROGRAM`, `PROJECT`, `SOURCE`, `UNIT` | 362 |

## Recommended Order

1. PLSQL extension hardening
2. Java Swing formal extension closure
3. COBOL/JCL split validation and packaging
4. Delphi/DFM extension cleanup

## Why PLSQL Next

PLSQL has enough inventory volume to benefit from the same workflow used for Java Frameworks: formal grammar path, FastParse extension, multithreaded MessagePack validation, encoding normalization, error/missing audits, and compact reports.

It should remain a separate grammar cycle because framework detection and PLSQL syntax do not share grammar rules, catalogs, or validation failure modes.

## Entry Criteria For The Next Cycle

- Confirm the target grammar path.
- Confirm whether work starts in `experimental-grammars/` or from an existing `grammars/` copy.
- Preserve a baseline before edits.
- Run corpus tests before inventory validation.
- Build the FastParse extension locally before full corpus runs.
- Store compact reports and clean temporary artifacts.
