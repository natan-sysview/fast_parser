# PERFORM TO Range

## Rule Name

`perform_procedure`

## Purpose

Accept Cementera COBOL/400 procedure ranges that use `TO` where the base grammar
already accepted `THRU`.

## Included Form

```cobol
PERFORM 025-GRAVA-LOG TO 025-FIM
```

## Excluded Forms

- Arbitrary `TO` clauses after `PERFORM` options.
- Changing the existing `THRU` tree shape.

## Local Syntax

`perform_procedure` accepts:

```text
<label> (THRU|TO) <label>
```

`TO` remains hidden in the public tree, matching the existing style for hidden
keywords in this grammar.

## Corpus

- `perform label to label`

## Audit Basis

Observed repeated errors in `PPOSIR103.sqlcbli` around:

```cobol
PERFORM 025-GRAVA-LOG TO 025-FIM
```
