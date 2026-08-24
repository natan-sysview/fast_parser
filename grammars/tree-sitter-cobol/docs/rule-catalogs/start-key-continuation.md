# Start Key Continuation

## Rule

`start_statement` with a `KEY IS NOT LESS THAN` condition may continue the key operand on the next physical line.

## Supported Form

```cobol
START DPREV412 KEY IS NOT LESS THAN
KEY-DPREV412.
```

The grammar already accepts the multiline statement. The FastParse COBOL AutoSafe normalizer must not insert a synthetic period between the `START` line and the key operand when the operand appears in Area A.

## Scope

- Included: `START <file> KEY ...` lines ending with an incomplete key comparator such as `KEY`, `EQUAL`, `GREATER`, `LESS`, `THAN`, or `NOT`.
- Included: next-line key operands that look like a bare COBOL label with period.
- Excluded: completed `START` statements followed by a real paragraph.

## Evidence

- Corpus: `procedure_tolerances/start key continuation in area a`.
- Runtime regression: `test_cobol_auto_safe_normalization_handles_fixed_layout_view_repairs`.
- Real file: `PSAP001.cbl` from Carlos.

