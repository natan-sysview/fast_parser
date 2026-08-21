# Accept Before Paragraph

## Rule name

`accept_statement` as the final statement before a following paragraph header.

## Purpose

Accept legacy procedure code where `ACCEPT ...` omits a terminating period before the next paragraph label.

## Included forms

- Existing supported `ACCEPT ... AT ... WITH ...` statements followed by a paragraph header.
- Existing supported `ACCEPT ... FROM DATE YYYYMMDD` statements followed by a paragraph header.

## Excluded forms

- No new `ACCEPT` operands or attributes are introduced.
- No broad "any statement before paragraph" tolerance is added.

## Local syntactic shapes supported

```cobol
           ACCEPT KDAT FROM DATE YYYYMMDD
       010-INICIALIZACAO.
           OPEN INPUT DMOVTO.
```

## Known semantic limits

This is a paragraph-boundary parse tolerance. It does not infer screen I/O behavior or insert a synthetic period.

## Corpus examples covered

- `accept without period before paragraph` in `test/corpus/procedure_tolerances.txt`.

## Audit result summary

Validation artifact: `runs/candidate_compare_current_cementera_accept_before_paragraph_20260821.sqlite`.

- Corpus: `256/256` passed.
- Cementera files: `4,169`.
- Parsed OK: `4,169`.
- Hard failures: `0`.
- ERROR nodes: `436 -> 417`.
- MISSING nodes: `3 -> 3`.
- File-level comparison: `20` improved, `1` exposed one additional residual error in an unrelated comma/continuation display block.

Decision: keep. The rule removes confirmed `ACCEPT ...` paragraph-boundary errors and does not introduce parser hard failures.
