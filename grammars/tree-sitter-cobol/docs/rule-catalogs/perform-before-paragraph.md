# Perform Before Paragraph

## Rule name

`perform_statement_call_proc` as the final statement before a following paragraph header.

## Purpose

Accept legacy procedure code where `PERFORM ...` omits a terminating period before the next paragraph label.

## Included forms

- `PERFORM <label> THRU <label> UNTIL <condition>` followed by a paragraph header.
- Existing supported `perform_statement_call_proc` shapes as the last statement before a header.

## Excluded forms

- No new `PERFORM` options are introduced.
- No broad "any statement before paragraph" tolerance is added.

## Local syntactic shapes supported

```cobol
           PERFORM 020-DACORD110 THRU 020-SAI UNTIL WFIM = 1
       FINALIZACAO.
           GOBACK.
```

## Known semantic limits

This is a paragraph-boundary parse tolerance. It does not infer control-flow semantics or insert a synthetic period.

## Corpus examples covered

- `perform without period before paragraph` in `test/corpus/procedure_tolerances.txt`.

## Audit result summary

Initial target: Cementera residual `PROCEDURE_PARAGRAPH` errors where paragraph headers follow `PERFORM ...` without a period. Full validation result is recorded in the corresponding `runs/` SQLite report after parser generation.
