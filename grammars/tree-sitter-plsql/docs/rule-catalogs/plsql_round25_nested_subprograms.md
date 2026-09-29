# PLSQL Round 25 Nested Subprograms

## Rule names

- `nested_procedure_definition`
- `nested_function_definition`

## Purpose

Expose PL/SQL subprograms declared inside procedure/function bodies as explicit
named nodes so downstream impact analysis can count local nested procedures and
functions without relying on ancestor heuristics over generic
`procedure_definition` or `function_definition` nodes.

## Included forms

- A procedure declared inside a procedure body declaration section.
- A function declared inside a procedure body declaration section.
- A procedure declared inside a function body declaration section.
- A function declared inside a function body declaration section.
- Recursive nesting, where a nested procedure/function contains additional
  nested procedures/functions.

## Excluded forms

- Package body member procedures/functions. These remain
  `procedure_definition` and `function_definition`.
- Package spec procedure/function declarations.
- Standalone `CREATE PROCEDURE` and `CREATE FUNCTION` roots.
- Anonymous block local subprograms. These still use the existing generic
  declaration rules unless they are inside a procedure/function body.

## Local syntactic shapes supported

Nested subprograms are recognized in the declaration section of
`_subprogram_body_with_declarations`, before the executable `body`. The syntax
matches the existing procedure/function definition forms, including parameter
lists, return declarations for functions, properties, `IS`/`AS`, call specs, and
recursive local declarations.

## Known semantic limits

The grammar marks a subprogram as nested when it appears in a procedure/function
body declaration section. It does not compute semantic ownership, call graphs,
or symbol resolution. Counts such as "how many nested subprograms a procedure
has" should be computed by traversing the AST under each outer subprogram.

## Corpus examples covered

- `Procedure with nested procedure and function`
- `Function with nested function and procedure`
- `Package body members stay non nested`

## Audit result summary

Full inventory audit found:

- Files with nested subprograms: 316.
- `nested_procedure_definition`: 942 nodes.
- `nested_function_definition`: 488 nodes.
- Total nested subprogram nodes: 1,430.
- Subprogram owners with direct nested subprograms: 497.
- Maximum nested depth: 3.
- Counter failures: 0.

By subtype:

| Subtype | Files | Owners with nested | Nested procedures | Nested functions | Total nested | Max depth |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FNC | 38 | 40 | 183 | 61 | 244 | 2 |
| PKB | 183 | 358 | 494 | 343 | 837 | 3 |
| PKS | 1 | 2 | 15 | 0 | 15 | 1 |
| PRC | 94 | 97 | 250 | 84 | 334 | 2 |

Owner context:

| Owner context | Owners |
| --- | ---: |
| Package body member procedures/functions | 334 |
| Standalone/create procedure roots | 94 |
| Standalone/create function roots | 38 |
| Nested subprograms that also own nested subprograms | 29 |
| Legacy package/spec-like package procedures | 2 |

`Total nested` counts nested definitions, not components and not outer
procedures. For PKB, 183 files contain 837 nested definitions owned by 358
subprogram bodies; 334 of those owners are package body members.

The PKS hit is a legacy `CREATE PACKAGE ... IS DECLARE ...` file whose subtype
comes from inventory classification; the nested nodes occur inside procedure
bodies within that file, not as package spec declarations.

## Validation

- Parser generation: passed.
- Corpus: 176/176 passing.
- Full inventory DB: `runs/plsql_native_validation_round25_nested_subprograms_threads8.sqlite`
- Inventory files: 13,258.
- Hard failures: 0.
- Files with `ERROR`: 0.
- Total `ERROR` nodes: 0.
- Files with `MISSING`: 0.
- Total `MISSING` nodes: 0.
- Encoding normalized: 1,268.
- Runtime with 8 threads: 27.39s.

## Decision

Stable as an experimental grammar enhancement. The rule adds useful named nodes
for impact analysis while preserving the zero-residual full-inventory baseline.
