# Rule Catalog: create_table

## Purpose

`create_table` recognizes Oracle relational `CREATE TABLE` DDL used by the CR inventory subtype.

## Included Forms

Initial supported syntax:

```text
CREATE TABLE [schema.]table_name (
  column_name datatype [DEFAULT expression] [NULL | NOT NULL] [inline constraint],
  [table constraint]
)
[common Oracle table options]
;
```

Included column datatype families reuse the existing PL/SQL `datatype` rule:

```text
VARCHAR2(n BYTE|CHAR)
CHAR(n BYTE|CHAR)
NVARCHAR2(n)
NCHAR(n)
NUMBER
NUMBER(p)
NUMBER(p,s)
DATE
DATE(n)
TIMESTAMP
LONG
LONG(n)
NUMBER(*,s)
CLOB[(n)]
BLOB[(n)]
BFILE
NCLOB
referenced/user datatypes
```

Included constraints:

```text
NOT NULL
NULL
PRIMARY KEY
UNIQUE
REFERENCES table [(columns)] [ON DELETE CASCADE | ON DELETE SET NULL]
CHECK (expression)
CONSTRAINT name <constraint>
ENABLE|DISABLE after NOT NULL or inline/table constraints
VALIDATE|NOVALIDATE in ALTER TABLE ADD constraint
```

Included table options:

```text
LOGGING
NOLOGGING
COMPRESS
NOCOMPRESS
CACHE
NOCACHE
PARALLEL
NOPARALLEL
MONITORING
NOMONITORING
TABLESPACE name
PCTFREE n
PCTUSED n
INITRANS n
MAXTRANS n
SEGMENT CREATION IMMEDIATE|DEFERRED
STORAGE (
  INITIAL nK|nM
  NEXT nK|nM
  MINEXTENTS n
  MAXEXTENTS n|UNLIMITED
  PCTINCREASE n
  BUFFER_POOL DEFAULT
)
NESTED TABLE column STORE AS storage_table
```

Included companion DDL commonly present in CR files:

```text
CREATE GLOBAL TEMPORARY TABLE ...
CREATE TABLE ... AS SELECT ...
CREATE [UNIQUE] INDEX name ON table (expression [ASC|DESC], ...)
CREATE [PUBLIC] SYNONYM name FOR object
CREATE SEQUENCE name ...
DROP TABLE name [CASCADE CONSTRAINT|CONSTRAINTS]
DROP [PUBLIC] SYNONYM name
DROP SEQUENCE name
TRUNCATE TABLE name
ALTER TABLE name DROP PRIMARY KEY [CASCADE]
ALTER TABLE name DROP CONSTRAINT name [CASCADE]
ALTER TABLE name ADD ([CONSTRAINT name] PRIMARY KEY|UNIQUE|FOREIGN KEY|CHECK ...)
ALTER TABLE name MODIFY (column datatype ...)
COMMENT ON TABLE|COLUMN object IS 'text'
GRANT privileges ON object TO grantees
GRANT CREATE TABLE|GLOBAL QUERY REWRITE TO grantees
SQL*Plus PROMPT, REM, SPOOL, EXIT, and SET DEFINE ON|OFF
anonymous PL/SQL blocks used around DROP TABLE
```

## Excluded For This Pass

These are intentionally deferred:

```text
CREATE PRIVATE TEMPORARY TABLE
ORGANIZATION EXTERNAL
ORGANIZATION INDEX
partitioning and subpartitioning
LOB storage clauses
complete physical STORAGE(...) grammar beyond observed options
standalone SQL*Plus slash as a generic statement outside supported script forms
```

## Known Limits

The rule is syntactic. It does not validate whether datatypes, constraints, or options are semantically valid for a specific Oracle version.

The table options are a first common subset from the local inventory audit, not a complete Oracle DDL grammar.

## Audit Basis

CR audit artifacts:

```text
audits/cr_syntax/README.md
audits/cr_syntax_after_create_table_ddl5
audits/cr_syntax_after_create_table_ddl9
runs/plsql_native_validation_cr_after_create_table_ddl9.sqlite
```

Baseline before CR repair: 6,794 CR files, 6,794 files with `ERROR`, 299,025 `ERROR` nodes, 26 `MISSING` nodes.

Final CR result for this rule pass: 6,794 CR files, 0 files with `ERROR`, 0 `ERROR` nodes, 0 files with `MISSING`, 0 `MISSING` nodes, and 39 encoding-normalized files.
