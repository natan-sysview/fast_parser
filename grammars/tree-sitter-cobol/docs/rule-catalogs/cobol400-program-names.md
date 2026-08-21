# cobol400-program-names

## Purpose

Allow `PROGRAM-ID` names that contain COBOL/400-style underscores.

## Basis

Cementera contains program names such as:

```cobol
PROGRAM-ID. PCALEND_TP.
PROGRAM-ID. PPALMPR_04.
```

The grammar already had `cobol400_word`, but `program_name` accepted only plain words or literals.

## Included Forms

- `PROGRAM-ID. <cobol400_word>.`
- Existing plain word and literal program names remain supported.

## Excluded Forms

- Arbitrary punctuation in program names beyond the existing `cobol400_word` shape.

## Grammar Shape

Extends `program_name` with `cobol400_word`.

## Corpus

- `identification_metadata.txt`
  - `program id with underscore`

## Smoke Result

Local normalized parses became clean for:

- `PCALEND_TP.sqlcbli`
- `PPALMPR_04.sqlcbli`

Full Cementera FastParse validation is required after rebuilding the extension.
