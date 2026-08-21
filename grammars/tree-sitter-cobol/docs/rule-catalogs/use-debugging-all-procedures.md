# use-debugging-all-procedures

## Purpose

Accept plural `PROCEDURES` in declarative debugging statements.

## Basis

IBM S/36 Cementera programs contain:

```cobol
USE FOR DEBUGGING ON ALL PROCEDURES.
```

The grammar already accepted the singular form `ALL PROCEDURE`, but not the plural keyword.

## Included Forms

- `USE FOR DEBUGGING ON ALL PROCEDURE`
- `USE FOR DEBUGGING ON ALL PROCEDURES`

## Excluded Forms

- Other `USE AFTER ERROR/EXCEPTION` variants.
- Procedure-name lists outside existing grammar support.

## Grammar Shape

Extends `_use_debugging` to accept hidden token `_PROCEDURES` in the existing `ALL ...` branch.

## Corpus

- `procedure_tolerances.txt`
  - `use debugging on all procedures plural`

## Smoke Result

Local normalized S/36 parses advance past `USE FOR DEBUGGING ON ALL PROCEDURES`; apparent matches on `ERROR` were ordinary identifiers such as `W-ERROR-CONDITION`, not Tree-sitter error nodes.

Full Cementera FastParse validation is required after rebuilding the extension.
