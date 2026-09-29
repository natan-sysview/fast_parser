# PLSQL residual repair round 12

Date: 2026-06-26

Scope: safe residual repairs after the round11 stable baseline.

## Rules added or changed

### Legacy fetch followed by exit without separator

Adds `legacy_fetch_exit_without_separator` to accept the conversion artifact:

```sql
FETCH v_cursor INTO v_result
EXIT WHEN v_cursor%NOTFOUND;
```

Reason: `PR_CREA_ARCHIVO_INI.sql` is missing the semicolon between a `FETCH` statement and an `EXIT WHEN` statement. The tolerance is scoped to exactly `fetch_statement` followed by `exit_statement`, so it does not loosen general statement boundaries.

Corpus: `Legacy fetch exit without separator`.

### Legacy parenthesized WITH select statement

Adds `legacy_parenthesized_with_select_statement` for package-body SQL shaped as:

```sql
WITH cfdi AS (
  SELECT 1 id FROM dual
)
(SELECT id INTO v_id FROM cfdi);
```

Reason: `PKG_FACTURAS.pkb` wraps a `WITH`-factored `SELECT INTO` in an extra parenthesized statement. The rule is placed in `_sql_statements`, not general expression parsing, so it stays tied to SQL statement context.

Corpus: `Legacy parenthesized WITH select statement`.

## Rejected patterns

The remaining FNC `GETSEXNIV.sql` errors are glued conversion tokens such as `IFp_tipo_mov`, `IFINSTR`, `=0THEN`, and `ENDIF`. A broad keyword-glue recovery was rejected because earlier probes made valid statement choices worse.

`CBA_AP_AUTOMATICO.pkb` contains embedded Java/pseudocode fragments such as `procedure patito`, `class PatitoDaoImpl`, Java-like string quoting, and test calls mixed into the package body. This should stay a source-normalization issue, not a grammar rule.

`PKGZDHH_CONTROL_BATCH.pkb` has an `INSERT` column list/value-list mismatch and a missing comma before `SIT_ENVIO_API`. Accepting that globally would hide real SQL mistakes.

`PKG_RAROC.pkb` and `PKG_WF_CREDITO.pks` are truncated before syntactic closure. They are better tracked as incomplete-source cases.

The ISR layout procedures still contain hard-wrapped prose/comment/string fragments. They need source normalization or a targeted preprocessor before further grammar repair.
