# COPY Statement

## Rule Name

`copy_statement`

## Purpose

Represent COBOL `COPY` as real syntax instead of treating it as global
whitespace. This prevents `COPY ... .` from hiding period terminators needed by
Data Division and Procedure Division rules.

## Included Forms

- `COPY member.`
- `COPY member OF library.`
- `COPY member library.`
- `COPY member SUPPRESS REPLACING ...`
- `COPY member REPLACING ...`
- `COPY "member.cpy".`

## Excluded Forms

- Copybook expansion.
- Resolving library search paths.
- Semantic validation of pseudo-text replacements.

## Local Syntax Supported

`copy_statement` no longer consumes the final period. The enclosing grammar
context owns the terminator:

- Data/copybook entries parse `copy_statement` followed by a data period.
- Procedure Division parses `copy_statement` as a normal statement followed by
  the common sentence terminator.
- File Section record layouts can parse `01 record-name` followed by
  `COPY layout OF library.` as one record-description list.

The `book` field is required. `lib_name`, `supress`, and `replacing_clause` are
optional. `lib_name` can appear with `OF`/`IN` or as the next bare copy target;
Cementera uses this for DDS forms such as `COPY DDS-ALL-FORMATS DCLINAT25.`.

## Corpus

- `test/corpus/copy_replacing.txt`
- `test/corpus/data_description.txt`

Covered cases include replacing identifier pairs, pseudo-text replacement,
procedure `COPY`, file-section `FD` copy layouts, linkage-section copy-only
bodies, and `01` record descriptions followed by `COPY`.

## Carlos Validation

The final Carlos validation is:
`runs/candidate_compare_current_carlos_copybook_exec_sql_zero_fixed_v4.sqlite`

This rule is required for `PCOMIS01.cbl`, where File Section records use:

```cobol
       01  R-DCOMIS01
           COPY DDS-ALL-FORMATS OF DCOMIS01.
```

It is also required in Procedure Division for:

```cobol
           COPY ENTRADA OF FPREV006.
```

Decision: keep `COPY` as explicit grammar structure in the experimental grammar.
