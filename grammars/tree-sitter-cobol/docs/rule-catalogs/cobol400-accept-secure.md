# COBOL/400 Accept Secure

## Rule name

`SECURE` in `with_accp_attr`.

## Purpose

Recognize COBOL/400 terminal input statements that use `SECURE` to hide typed input in `ACCEPT ... WITH` clauses.

## Included forms

- `ACCEPT WSENHA01 AT 1937 WITH SECURE.`
- `ACCEPT WS-CAMPO WITH AUTO-SKIP SECURE.`

## Excluded forms

- `SECURE` outside `ACCEPT ... WITH` attributes.
- Display attributes for `DISPLAY ... WITH`.

## Local syntactic shapes supported

```cobol
           ACCEPT WSENHA01 AT 1937 WITH SECURE.
```

## Known semantic limits

This rule recognizes the syntax only. It does not infer screen privacy semantics.

## Corpus examples covered

- `accept with secure attribute` in `test/corpus/cobol400_accept_space_fill.txt`.

## Audit result summary

Validation artifact: `runs/candidate_compare_current_cementera_accept_secure_20260821.sqlite`.

- Corpus: `257/257` passed.
- Cementera files: `4,169`.
- Parsed OK: `4,169`.
- Hard failures: `0`.
- ERROR nodes: `417 -> 413`.
- MISSING nodes: `3 -> 3`.
- File-level comparison: `4` improved, `0` regressed.

Decision: keep. The rule removes confirmed `ACCEPT ... WITH SECURE` password/input errors without broadening other statement parsing.
