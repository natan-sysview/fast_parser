# computer-name-dialects

## Purpose

Accept common COBOL environment computer-name dialect forms used by AS/400 and IBM S/36 sources.

## Basis

Cementera contains:

- `SOURCE-COMPUTER. AS/400.`
- `OBJECT-COMPUTER. AS/400.`
- `SOURCE-COMPUTER. IBM-S36 WITH DEBUGGING MODE.`
- `OBJECT-COMPUTER. IBM-S36 MEMORY 22528 CHARACTERS.`

The previous grammar accepted plain `WORD` names and Burroughs names, but not slash names, and required `MEMORY SIZE ...`.

## Included Forms

- Computer names with slash, such as `AS/400`.
- Existing word names such as `AS-400`, `IBM-AS400`, and `IBM-S36`.
- `OBJECT-COMPUTER ... MEMORY <integer> CHARACTERS` without the optional `SIZE` keyword.

## Excluded Forms

- Arbitrary slash identifiers outside `SOURCE-COMPUTER` and `OBJECT-COMPUTER`.
- Other object-computer clauses not already modeled by the grammar.

## Grammar Shape

Adds `computer_name_with_slash` and internal helper `_computer_name`. Makes `SIZE` optional in `object_computer_memory`.

## Corpus

- `source-object-computer.txt`
  - `source and object computer as slash 400`
  - `object computer memory without size`

## Smoke Result

Local normalized parse of `PCALEND05.sqlcbli` became clean. S/36 samples advance past `OBJECT-COMPUTER` and now expose a separate `USE ... ON ALL PROCEDURES` residual.

Full Cementera FastParse validation is required after rebuilding the extension.
