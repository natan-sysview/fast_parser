# Display With Before At

## Rule name

`display_statement` with `with_clause` before `at_line_column`.

## Purpose

Recognize COBOL/400 screen display statements where display attributes are written before the screen position.

## Included forms

- `DISPLAY "text" WITH REVERSE-VIDEO AT 1620.`
- Existing `WITH` attribute lists followed by an `AT` screen position.

## Excluded forms

- Display paragraph-boundary recovery.
- New display attributes; this rule only changes clause ordering.
- `ACCEPT` statements, which are handled separately.

## Local syntactic shapes supported

```cobol
           DISPLAY "Deseja excluir?" WITH REVERSE-VIDEO AT 1620.
```

## Known semantic limits

This rule recognizes clause order only. It does not validate terminal capabilities or screen coordinates.

## Corpus examples covered

- `display with attributes before at` in `test/corpus/display_tolerances.txt`.

## Audit result summary

Validation artifact: `runs/candidate_compare_current_cementera_display_with_before_at_20260821.sqlite`.

- Corpus: `260/260` passed.
- Cementera files: `4,169`.
- Parsed OK: `4,169`.
- Hard failures: `0`.
- ERROR nodes: `410 -> 389`.
- MISSING nodes: `3 -> 3`.
- File-level comparison: `23` improved, `1` regressed.

Regression note: `PPREV100.sqlcbli` changed from `1` to `3` residual errors in a later multiline `DISPLAY` block with many `"text" AT nnnn` items. The net result still removes `21` ERROR nodes; the remaining multiline display block is tracked for a separate display-item repair.

Decision: keep. The rule fixes common COBOL/400 `DISPLAY ... WITH ... AT ...` ordering and substantially lowers Cementera errors.
