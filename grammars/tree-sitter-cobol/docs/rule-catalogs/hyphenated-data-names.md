# Hyphenated Data Names

## Rule Name

`_WORD`

## Purpose

Accept standard COBOL data-names that contain internal hyphens, including
names ending with numeric segments observed in Cementera sources.

## Included Forms

```cobol
CDLOC-102
WS-STATUS-VAR
WS-FUNC-03
AS-400
```

## Excluded Forms

- Names ending in a hyphen.
- Pure numeric paragraph labels, which remain covered by `numeric_label` or
  integer forms depending on context.

## Local Syntax

The `_WORD` token now accepts letter-starting names with internal hyphens while
requiring the final character to be alphanumeric.

## Corpus

- `hyphenated data name in class condition`
- `hyphenated data name with abbreviated numeric list`

## Audit Basis

Observed Cementera errors around:

```cobol
IF CDLOC-102 IS NOT NUMERIC
IF CDLOC-102 NOT EQUAL 01 AND 03 AND 13 AND 20
MOVE "ERRO" TO WS-STATUS-VAR
```

This is a broad lexical improvement and must be validated against the full
COBOL inventory before being accepted as stable.
