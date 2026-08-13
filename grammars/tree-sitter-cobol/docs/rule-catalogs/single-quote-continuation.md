# Single-Quote Continuation Literals

## Rule Name

`_multiline_string`

## Purpose

Recognize fixed-format COBOL continued string literals that use single quotes.

## Basis

Residual `DATA_DESCRIPTION` samples after the label-record variants repair showed continuation forms such as:

```cobol
026930        ' SUCURSAL DIVISION BANCA       TIPO SUBTIPO FOLIO  FECHA
026930-       '     HORA    NOMBRE COMERCIAL       STATUS STATUS FECHA
```

The existing external scanner already supported the same fixed-format continuation shape for double-quoted strings.

## Included Forms

- Long single-quoted literals that reach the fixed-format continuation boundary.
- Continuation lines with a hyphen in indicator column 7 followed by optional spaces and another single quote.
- Existing double-quoted continuation behavior remains unchanged.

## Excluded Forms

- Short unterminated literals that end before the fixed-format boundary.
- Semantic concatenation of literal text.
- Continuations for `X'...'`, `N'...'`, or `H'...'` prefixed literals.

## Local Syntax Supported

The scanner now captures the opening quote delimiter, either `'` or `"`, and uses it consistently while scanning continuation lines.

## Known Limits

The scanner preserves the existing fixed-format assumption: continuation is recognized only when the first literal line reaches the continuation boundary before the closing quote.

## Audit Result Summary

Validation date: 2026-06-26.

- Corpus: 107/107 passed.
- Full COBOL inventory: 74,151 files parsed OK.
- Hard failures: 0.
- Files with `ERROR`: 35,233 -> 34,303.
- `ERROR` nodes: 40,288 -> 38,744.
- Files with `MISSING`: 18 -> 18.
- `MISSING` nodes: 18 -> 18.
- Files with any Tree-sitter issue: 35,241 -> 34,311.
- Became clean by `ERROR` nodes: 930 files.
- Became dirty by `ERROR` nodes: 0 files.

The first implementation accepted single quotes but did not consume adjacent quote segments such as `''''`, which created new errors in `INSPECT ... BY ''''` patterns. V2 consumes adjacent quoted segments before returning the scanner token.
