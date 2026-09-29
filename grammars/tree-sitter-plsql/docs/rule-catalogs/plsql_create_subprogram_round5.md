# PLSQL Create Subprogram Round 5

## Rule name

`create_function`, `create_procedure`, Java call specs, and converted select aliases.

## Purpose

Recover top-level Oracle `CREATE FUNCTION` and `CREATE PROCEDURE` files that were being wrapped in root `ERROR` nodes after their `BEGIN ... END` body was parsed.

## Basis

Enterprise inventory evidence from PRC/FNC components showed the parser recognized `CREATE OR REPLACE ...` headers but required an extra `END` after `body`. Oracle call specs also terminate with `;`, not with `END`.

## Included forms

- `CREATE OR REPLACE PROCEDURE ... IS BEGIN ... END name;`
- Quoted schema and object names such as `"SEUS"."P_TEST"`.
- `CREATE OR REPLACE EDITIONABLE FUNCTION ... RETURN ... AUTHID CURRENT_USER AS LANGUAGE JAVA NAME '...';`
- Converted select aliases written as `\ALIAS\` in select lists.

## Excluded forms

- Source normalization of malformed tokens such as `0THEN`, `IFp_tipo`, or `ENDIF`.
- Semantic validation of Java method signatures inside `LANGUAGE JAVA NAME`.
- Treating `\ALIAS\` as official Oracle SQL syntax outside converted enterprise select lists.

## Local syntactic shapes supported

- `create_function` and `create_procedure` now split body and call-spec alternatives:
  - PL/SQL body alternative consumes `body`, whose `END ...;` is already included.
  - Call-spec alternative consumes `call_spec_ext` followed by `;`.
- Function properties include `AUTHID CURRENT_USER` / `AUTHID DEFINER`.
- Select-list aliases accept a narrow `backslash_quoted_identifier`.

## Corpus examples covered

- `Create procedure with quoted schema`
- `Create editionable function with quoted schema`
- `Backslash quoted select aliases`
- `Create Java call spec function`

## Audit result summary

Full inventory stayed at 13,258 PLSQL files with 0 hard failures. CR remained 0 ERROR / 0 MISSING.

Compared with the pre-round validation:

- FNC files with ERROR dropped from 567 to 17.
- FNC ERROR nodes dropped from 602 to 52.
- PRC files with ERROR dropped from 3,225 to 1,002.
- PRC ERROR nodes dropped from 4,929 to 1,760.
- PKB and PKS ERROR counts stayed unchanged.

Remaining FNC issues are mostly malformed converted code (`0THEN`, `IF...` glued to identifiers, `ENDIF`) and a small set of root recovery cases requiring separate analysis.
