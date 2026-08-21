# SPECIAL-NAMES Comma-Separated Entries

## Rule Name

`special_names_paragraph`

## Purpose

Recognize COBOL `SPECIAL-NAMES` paragraphs where entries are separated with a comma, as seen in Cementera AS/400 sources.

## Included Form

```cobol
SPECIAL-NAMES.
    DECIMAL-POINT IS COMMA
    CONSOLE IS CRT, CRT STATUS IS WS-CRT-STATUS.
```

## Excluded Forms

- Semantic validation of console device names.
- Treating arbitrary comma-separated text as a special-name entry.

## Corpus

- `special names comma separated crt status`

## Audit Basis

Observed in `PGRID001.sqlcbli`, where `CONSOLE IS CRT, CRT STATUS IS WS-CRT-STATUS` caused whole-file recovery in the Cementera validation.
