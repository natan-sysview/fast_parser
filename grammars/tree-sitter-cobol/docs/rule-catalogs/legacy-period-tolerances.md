# Legacy Period Tolerances

## Rule Names

- `data_description_without_period`
- `_procedure_division_statements_before_header`

## Purpose

Handle legacy COBOL sources that omit a period at a local boundary while keeping
the tolerance visible in the syntax tree or tightly scoped in procedure parsing.

## Included Forms

### Data Description Without Period

```cobol
       01 GROUP-A.
          03 FIELD-A PIC X VALUE SPACE
          03 FIELD-B PIC X VALUE SPACES.
```

The first `03` is exposed as `data_description_without_period`.

### REWRITE Before Paragraph Header

```cobol
       100-A.
           REWRITE R-REC
       100-B.
           EXIT.
```

This accepts a `rewrite_statement` immediately before the next paragraph header.

## Excluded Forms

- Broadly accepting every missing period in Procedure Division.
- Treating arbitrary malformed Data Division entries as valid.
- Hiding the tolerance as a generic catch-all `ERROR` recovery.

## Local Syntax Supported

`data_description_without_period` has low precedence, so normal
period-terminated entries continue to parse through the standard
`data_description` path.

The Procedure Division tolerance is intentionally scoped to `rewrite_statement`
before a header because that is the concrete Carlos pattern. Broader missing
period support should be added only after a separate audit finds more families.

## Corpus

- `test/corpus/data_description.txt`
- `test/corpus/procedure_tolerances.txt`

## Carlos Validation

Relevant file: `PCOMIS01.cbl`.

Final validation DB:
`runs/candidate_compare_current_carlos_copybook_exec_sql_zero_fixed_v4.sqlite`

- PROGRAM files: 51.
- PROGRAM files with `ERROR`: 0.
- PROGRAM `ERROR` nodes: 0.
- PROGRAM `MISSING` nodes: 0.

Decision: keep these tolerances named/scoped in the experimental grammar.
