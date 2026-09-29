# tree-sitter-plsql

Tree-sitter grammar for Oracle PL/SQL and the SQL/DDL constructs commonly embedded in PL/SQL repositories.

This vendored copy is the promoted FastParser PL/SQL grammar. It is scoped to pure Oracle PL/SQL source files; converted Oracle Forms exports are intentionally outside this grammar and should be handled by a separate Oracle Forms grammar.

## Coverage

- `CREATE`, `ALTER`, and `DROP` statements for packages, procedures, functions, triggers, types, libraries, views, sequences, synonyms, indexes, and tables.
- PL/SQL package specifications and package bodies.
- Top-level and nested procedures/functions.
- Common DML: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, and `MERGE`.
- Practical Oracle DDL details found in inventory validation, including table constraints, partitions, storage clauses, LOB clauses, and comments.

## Validation

The grammar is validated through the FastParser language-extension pipeline and local corpus fixtures under `test/corpus`.

## References

- [Oracle Database PL/SQL Language Reference](https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/index.html)
- [Oracle Database SQL Language Reference](https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/index.html)
