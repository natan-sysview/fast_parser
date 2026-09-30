# Oracle SQL object types and type bodies

## Scope

Rules: `create_type`, `create_type_body`, `type_constructor_definition`,
`type_member_function_definition`, and `type_member_procedure_definition`.

Basis: Oracle 19c [CREATE TYPE](https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/CREATE-TYPE-statement.html)
and [CREATE TYPE BODY](https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/CREATE-TYPE-BODY-statement.html).

Included forms:

- `AS`/`IS OBJECT (...)`, `UNDER parent (...)`, `AS`/`IS TABLE OF`, and `VARRAY`.
- A type specification ends with `;`; it does not require `END`.
- Repeated inheritance modifiers, such as `NOT FINAL NOT INSTANTIABLE`.
- A type body contains semicolon-terminated constructor or member method bodies,
  followed by its own `END;`.
- Quoted, schema-qualified names and Oracle editionability modifiers.

The constructor and member definitions are named nodes with name fields. Their
declarations, statements, and calls remain traversable. This is syntax only:
the grammar does not resolve overloads, inheritance, or type identity.

Excluded: malformed grants, provider bodies excluded by the assessment, and
files rejected before parsing. A package or procedure cannot use the type
specification's terminator in place of its own `END;`.

Corpus: `test/corpus/oracle_types.txt` covers object, collection, subtype,
constructor, member method, complete package, and invalid package-style
termination. `test/corpus/create_table.txt` guards nearby non-type DDL.

Validation: the full parser lab inventory and a separate Oracle-object
assessment were audited with FastParse MessagePack diagnostics. The local
audit records source hashes, error counts, missing counts, and node matches;
client source files and path-level evidence are not part of this catalog.
