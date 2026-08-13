# Rule Catalog: EXEC SQL

Status: proposed first repair batch.

## Goal

Recognize embedded DB2 SQL blocks in COBOL without trying to fully parse SQL semantics in the first iteration.

The immediate objective is to stop `EXEC SQL ... END-EXEC` from producing cascaded `ERROR` nodes, especially when SQL contains COBOL host variables.

## Intended Nodes

- `exec_sql_statement`
- `exec_sql_include`
- `sql_host_variable`

## Accepted Forms

### Include

```cobol
     EXEC SQL
         INCLUDE SQLCA
     END-EXEC.
```

```cobol
     EXEC SQL INCLUDE BGGTOPT END-EXEC.
```

```cobol
     EXEC SQL INCLUDE SQLCA END-EXEC..
```

### SQL Statement Body

```cobol
     EXEC SQL
         INSERT INTO BGDTOPT
         VALUES (:OPT-CODAPLI,
                 :OPT-FECIMP,
                 :OPT-NUMEROFIC)
     END-EXEC.
```

DB2 operator tokens accepted inside the generic SQL body include comparison
operators, `||`, and the single pipe `|` form observed in Carlos
`PCXA017.cbl`:

```cobol
     EXEC SQL
         SELECT A | B
           INTO :C
           FROM T
     END-EXEC.
```

```cobol
     EXEC SQL
         SELECT CAMPO
           INTO :WS-CAMPO
           FROM TABLA
          WHERE LLAVE = :WS-LLAVE
     END-EXEC.
```

### Host Variables

```cobol
:OPT-CODAPLI
:WS-CAMPO
:TABLA-CAMPO(WS-IDX)
```

## Excluded From First Batch

- Full SQL grammar for DB2.
- Semantic validation of table names, column names, or host variables.
- SQL precompiler directives outside `EXEC SQL ... END-EXEC`.
- Double Data Division terminators after generic SQL statement bodies. The
  accepted double-period repair is limited to `EXEC SQL INCLUDE`.
- CICS grammar, except that `EXEC CICS` should remain separate and not be swallowed as SQL.

## Negative Examples

These should not become `exec_sql_statement`:

```cobol
     EXEC CICS
         SEND MAP('X')
     END-EXEC.
```

```cobol
     MOVE ':NOT-SQL' TO WS-TEXT.
```

```cobol
     COPY SQLCA.
```

## Validation Targets

Top real files from the baseline audit:

- `/Users/natanbarronlugo/Desktop/Proyectos/appbatch/migracion_utilerias_sysmining/componentes/fuentes/mex/mexsrc/CBL/BG4CEST0`
- `/Users/natanbarronlugo/Desktop/Proyectos/appbatch/migracion_utilerias_sysmining/componentes/fuentes/mex/mexsrc/CBL/GM4C9901`
- `/Users/natanbarronlugo/Desktop/Proyectos/appbatch/migracion_utilerias_sysmining/componentes/fuentes/mex/mexsrc/CBL/GM4C9906`
- `/Users/natanbarronlugo/Desktop/Proyectos/appbatch/migracion_utilerias_sysmining/componentes/fuentes/mex/mexsrc/CBL/MF4C4310`
- `/Users/natanbarronlugo/Desktop/Proyectos/appbatch/migracion_utilerias_sysmining/componentes/fuentes/mex/mexsrc/CBL/AB4CCRN0`

## Baseline Metrics

Full baseline:

- Files: 74,151.
- Files with `ERROR`: 66,036.
- `ERROR` nodes: 143,202.
- Files with `MISSING`: 1,501.
- `MISSING` nodes: 1,553.

Relevant families:

- `EXEC_SQL_HOST_VARIABLES`: 61,738 `ERROR` nodes.
- `EXEC_SQL_INCLUDE`: 29,773 `ERROR` nodes.
- `EXEC_SQL_STATEMENT`: 1,381 `ERROR` nodes.

## Repair Result

Implemented on 2026-06-25 in the experimental grammar only.

Validation:

- `tree-sitter generate`: passed.
- `tree-sitter test`: all `exec_sql` corpus cases passed; one pre-existing `comment/comment` failure remains.
- Full FastParse diagnostics: 74,151 files, 74,151 parsed OK, 0 hard failures.
- Full FastParse binary validation: 74,151 files, 74,151 parsed OK, 0 hard failures.

Metric change:

| Metric | Before | After |
| --- | ---: | ---: |
| Files with `ERROR` | 66,036 | 59,349 |
| `ERROR` nodes | 143,202 | 82,580 |
| Files with `MISSING` | 1,501 | 1,691 |
| `MISSING` nodes | 1,553 | 1,719 |
| SQL_COBOL `ERROR` nodes | 122,727 | 64,169 |
| `EXEC_SQL_HOST_VARIABLES` family | 61,738 | 325 |
| `EXEC_SQL_INCLUDE` family | 29,773 | 351 |

Decision: keep the rule in the experimental grammar. Do not promote yet; inspect regressions and continue residual-family repairs.

## Data Division Include Double Period Repair

Implemented on 2026-06-30 in the experimental grammar only.

Purpose:

- Accept `EXEC SQL INCLUDE ... END-EXEC..` in Data Division.
- Keep the public tree shape as `exec_sql_statement`.
- Avoid broadening generic `EXEC SQL` body recovery.

Implementation:

- Added hidden `_exec_sql_include_statement`.
- Used `alias($._exec_sql_include_statement, $.exec_sql_statement)` in
  `_data_division_entry`.
- Allowed zero, one, or two Data Division terminators for that include-only
  entry.

Validation:

- `tree-sitter generate`: passed with the existing ABI 14 warning.
- `tree-sitter test --overview-only`: 167/167 passed.
- Full FastParse validation: 74,151 files, 74,151 parsed OK, 0 hard failures.
- Candidate validation DB:
  `runs/candidate_compare_current_exec_sql_include_data_double_period_full.sqlite`

Metric change versus
`runs/candidate_compare_current_fixed_format_counted_picture9_retry_post_skip_full.sqlite`:

| Metric | Before | After | Delta |
| --- | ---: | ---: | ---: |
| Files with `has_errors` | 3,161 | 3,159 | -2 |
| Files with `ERROR` nodes | 3,156 | 3,154 | -2 |
| `ERROR` nodes | 3,812 | 3,817 | +5 |
| Files with `MISSING` | 1 | 1 | 0 |
| `MISSING` nodes | 1 | 1 | 0 |
| `error_byte_count` | 313,055,297 | 313,052,632 | -2,665 |

Changed-file summary:

- Became clean: `EP4CXK03`, `RL5C0021`.
- Became dirty: none.
- Higher-node files: 9, all already dirty, all with lower `error_byte_count`.

Rejected broader variants:

- Unbounded `repeat($._data_period)` after any Data Division `EXEC SQL`:
  fixed the same two files but increased `ERROR` nodes by 13.
- Bounded zero/one/two periods after any Data Division `EXEC SQL`:
  fixed the same two files but increased `ERROR` nodes by 8.

Decision: keep the include-only repair in the experimental grammar. Treat the
9 higher-node files as a separate large recovery-family problem instead of
broadening this rule.

## Success Criteria

- `tree-sitter generate` succeeds.
- Corpus examples for accepted and negative forms pass.
- Top SQL_COBOL files reduce `ERROR` nodes without new hard failures.
- Full inventory validation has zero hard failures.
- `ERROR` and `MISSING` totals improve or any regression is explained with examples.

## Carlos Project Repair Addendum

Implemented on 2026-08-11 in the experimental grammar only.

Additional accepted forms:

- `EXEC SQL` generic DB2 body with single pipe `|`.
- `EXEC SQL INCLUDE` inside copybook/data entries.

Validation:

- Corpus: 178/178 passed.
- Carlos FastParse validation DB:
  `runs/candidate_compare_current_carlos_copybook_exec_sql_zero_fixed_v4.sqlite`
- Carlos files: 91.
- Parsed OK: 91.
- Hard failures: 0.
- SQL_COBOL files with `ERROR`: 0/2.
- SQL_COBOL `ERROR` nodes: 0.
- SQL_COBOL `MISSING` nodes: 0.

Decision: keep the DB2 operator/token support in the experimental grammar.
This is still a generic embedded-SQL body recognizer, not a full DB2 grammar.
