# XML, Transaction Organization, And ACQUIRE

## Rule Names

- `xml_generate_statement`
- `xml_parse_statement`
- `organization_clause`
- `acquire_statement`

## Purpose

Cover COBOL dialect constructs observed in Carlos sources without making a
catch-all procedure parser.

## Included Forms

### XML

```cobol
       XML GENERATE WS-XML FROM WS-DOC
          ON EXCEPTION CONTINUE
          NOT ON EXCEPTION CONTINUE
       END-XML.
```

```cobol
       XML PARSE WS-XML PROCESSING PROCEDURE P7000-XML-EVENT
          ON EXCEPTION CONTINUE
          NOT ON EXCEPTION CONTINUE
       END-XML.
```

### Transaction Organization

```cobol
       SELECT TRN-FILE ASSIGN TO WORKSTATION-ZCOVTRN
          ORGANIZATION IS TRANSACTION
          ACCESS MODE IS SEQUENTIAL
          FILE STATUS IS WS-TRN-ST.
```

### ACQUIRE

```cobol
       ACQUIRE 'QPADEV000R' FOR TRN-FILE.
       ACQUIRE WS-DEV FOR TRN-FILE.
```

## Excluded Forms

- Full XML event semantics.
- Validating whether the named processing procedure exists.
- Device/session semantics for `ACQUIRE`.
- Nonlocal file-control validation.

## Local Syntax Supported

`XML` is reserved as a keyword with lexical precedence so it is not parsed as a
paragraph name. XML handlers reuse existing procedure handler nodes
(`on_exception`, `not_on_exception`) and the common `END_XML` terminator.

`TRANSACTION` is a named alternative in `organization_clause`.

`acquire_statement` stores the acquired terminal/device as `terminal` and the
optional target file as `file_name`.

## Corpus

- `test/corpus/xml_transaction.txt`

## Carlos Validation

Validation DB:
`runs/candidate_compare_current_carlos_copybook_exec_sql_zero_fixed_v4.sqlite`

Relevant files:

- `ZCOVSPEC.cbl`: XML GENERATE/PARSE.
- `ZCOVTRAN.cbl`: `ORGANIZATION IS TRANSACTION` and `ACQUIRE`.

Final Carlos result:

- PROGRAM files with `ERROR`: 0/51.
- SQL_COBOL files with `ERROR`: 0/2.
- Total `ERROR` nodes: 0.
- Total `MISSING` nodes: 0.

Decision: keep these focused rules in the experimental grammar.
