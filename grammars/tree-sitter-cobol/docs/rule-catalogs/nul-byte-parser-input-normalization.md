# NUL Byte Parser Input Normalization

Status: stable experimental parser-input normalization.

## Goal

Allow COBOL sources containing raw `0x00` bytes to be parsed without treating
the byte as an end-of-input signal inside Tree-sitter lexing.

Original source bytes are preserved. The normalization applies only to the
parser input view used by validation.

## Included Forms

- Raw NUL byte inside a quoted literal:

```text
'<NUL>'
```

is passed to the parser as:

```text
'\0'
```

- Raw NUL byte outside a quoted literal is passed as a space.

## Excluded Forms

- Source file rewrite.
- Semantic conversion to COBOL hex notation.
- Broad escaping of every control byte.
- Changes to `grammar.js` or generated parser artifacts.

## Local Behavior

The normalizer scans UTF-8 parser input after decoding and after layout
trimming/blanking. It tracks single-quoted and double-quoted literals. Doubled
quote characters remain part of the active literal.

## Validation Result

Validated on 2026-08-14 against the COBOL inventory of 74,242 files.

- Parsed OK: 74,242.
- Hard failures: 0.
- Files with `ERROR`: 2,312 before, 2,249 after.
- `ERROR` nodes: 2,944 before, 2,622 after.
- Files with `MISSING`: 0 before, 0 after.
- `MISSING` nodes: 0 before, 0 after.
- Changed files: 66 improved, 0 regressed.

Representative improvements:

- `JY2CJYK2`: 45 `ERROR` nodes to 0.
- `BCWPLUT2`: 12 `ERROR` nodes to 0.
- `PE3CCA13`: 5 `ERROR` nodes to 0.

## Artifacts

- Report: `runs/cobol_nul_byte_parser_input_normalization_report.md`
- Validation DB: `runs/candidate_compare_current_nul_byte_parser_input_normalization_20260814.sqlite`
- Audit: `audits/nul_byte_parser_input_normalization_20260814/`

Decision: stable experimental parser-input normalization.
