# PLSQL Round 27 Stray Suffix Immediate Recovery

## Rule Name

`legacy_plsql_block_statement_with_stray_suffix` with `legacy_immediate_stray_statement_suffix_token`.

## Purpose

Keep support for true legacy text shaped like `END;x` while preventing the
recovery rule from crossing line breaks and consuming valid following statements
such as `ELSE` or `RETURN`.

## Basis

Round 26 quality audit found 2,344 `legacy_plsql_block_statement_with_stray_suffix`
nodes in 700 files. Manual samples showed most were valid PL/SQL anonymous
blocks inside `IF` or subprogram bodies, followed by normal `ELSE` or `RETURN`
syntax on later lines.

## Included Forms

- A PL/SQL block ending with `END` immediately followed by a semicolon and a
  stray identifier with no whitespace, for example `END;x`.
- The token is exposed through the existing public alias
  `legacy_stray_statement_suffix`.

## Excluded Forms

- Valid anonymous block statement followed by `ELSE` on another line.
- Valid anonymous block statement followed by `RETURN` on another line.
- Any block where the semicolon and next identifier are separated by whitespace
  or comments.
- Semantic interpretation of the stray suffix.

## Supported Local Shape

```plsql
BEGIN
  NULL;
END;x
```

The grammar now models `;x` as one immediate recovery token after `plsql_block`,
instead of parsing `;` and then accepting a later generic identifier.

## Corpus Coverage

- `Legacy block end stray suffix` keeps the `END;x` recovery.
- `Anonymous block before ELSE is normal IF syntax` proves that
  `BEGIN ... END; ELSE ... END IF;` stays normal PL/SQL structure.
- Existing negative regression `Adjacent DML column without legacy token stays
  erroneous` still passes.

## Audit Result Summary

Round 27 full inventory validation:

- Files: 13,258.
- Lines: 4,556,560.
- Hard failures: 0.
- `ERROR` nodes: 0.
- `MISSING` nodes: 0.
- Encoding-normalized files: 1,268.

Legacy-node comparison:

- Round 26 total legacy nodes: 18,013 in 1,623 files.
- Round 27 total legacy nodes: 13,323 in 956 files.
- `legacy_plsql_block_statement_with_stray_suffix`: 2,344 nodes in 700 files
  down to 1 node in 1 file.
- `legacy_stray_statement_suffix`: 2,344 nodes in 700 files down to 1 node in
  1 file.

The remaining match is a true `END;x` artifact in:

```text
/Users/natanbarronlugo/Desktop/Proyectos/componentes/metlife-provida-sin-externos/entregables/Metlife2ApocProC/Componentes/ENV_CBA_PACKAGE.pkb
```

## Decision

Stable for the experimental grammar. The rule is now narrow enough to preserve
the known legacy artifact without degrading normal PL/SQL control-flow ASTs.
