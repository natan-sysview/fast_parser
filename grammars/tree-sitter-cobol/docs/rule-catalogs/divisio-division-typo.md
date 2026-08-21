# divisio-division-typo

## Purpose

Accept the legacy typo `DIVISIO` as `DIVISION` in division headers.

## Basis

One residual Cementera file contains:

```cobol
PROCEDURE DIVISIO.
```

This prevents the procedure division from being recognized and leaves the rest of the program in recovery.

## Included Forms

- `DIVISION`
- `DIVISIO`

## Excluded Forms

- Other division keyword misspellings.
- Changing the required division header structure.

## Grammar Shape

Extends hidden token `_DIVISION` with a second spelling for `DIVISIO`.

## Corpus

- `minimal-cobol.txt`
  - `Minimal COBOL program with truncated procedure divisio`

## Audit Result

Full Cementera validation `runs/candidate_compare_current_cementera_divisio_typo_20260821.sqlite` reduced total `ERROR` nodes from 173 to 172 and files with `ERROR` from 198 to 197, with zero `MISSING` nodes before and after. Improved file:

- `GTC05.sqlcbli`

No regressions were found.
