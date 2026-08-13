# Rule Catalog: At-Hex Literal

Status: implemented in experimental grammar.

## Rule Name

`at_hex_literal`

## Purpose

Recognize Burroughs/Unisys-style hexadecimal byte literals written as
`@..@`, primarily in data-description `VALUE` clauses.

## Basis

During the deferred `ACTUAL KEY` experiment, several legacy `OBJECT` programs
parsed farther into their data division and exposed errors at values such as:

```cobol
       01 CTT-EOFI PIC 9(02) COMP VALUE @0D@.
       01 WKS-NULO-HEX PIC 9(02) COMP VALUE @00@.
```

A targeted source scan of the `OBJECT` sources found 1,279
`@[0-9A-Fa-f]+@` values in 13 files, including long byte tables in
`P108_12MTP004`.

## Included Forms

```text
@[0-9A-Fa-f]+@
```

Examples:

- `@00@`
- `@0D@`
- `@6A@`
- `@8F@`

## Excluded Forms

- Validation that the number of hex digits is even.
- Mapping the literal to a character encoding or byte value.
- Non-hex payloads between `@` delimiters.
- General use of `@` outside literal contexts.

## Grammar Shape

`at_hex_literal` is added to `_basic_value`, so existing `value_item` handling
accepts it without changing the shape of `value_clause`.

```text
VALUE @0D@
```

## Corpus Coverage

- Data-description `VALUE @0D@` after `PIC 9(02) COMP`.

## Validation Plan

1. Generate parser artifacts.
2. Run full corpus tests.
3. Smoke parse `OBJECT` files that previously exposed `VALUE @..@` errors.
4. Rebuild the FastParse COBOL language extension.
5. Re-run full inventory validation against the current stable baseline.
6. Accept only if `ERROR`/`MISSING` totals do not regress.

## Validation Result

Validated on 2026-06-30 as part of the
`current_burroughs_computer_at_hex_no_actual_key` candidate.

- `tree-sitter generate`: passed with the pre-existing ABI 14 warning.
- `tree-sitter test --overview-only`: 162/162 passed.
- Full inventory DB:
  `runs/candidate_compare_current_burroughs_computer_at_hex_no_actual_key_full.sqlite`
- Parsed OK: 74,151.
- Hard failures: 0.
- Files with `ERROR`: 10,401 -> 10,401.
- `ERROR` nodes: 11,328 -> 11,325.
- Files with `MISSING`: 1 -> 1.
- `MISSING` nodes: 1 -> 1.

Parse-visible audit in the final candidate found 0 `at_hex_literal` nodes in
the 34 `OBJECT` programs. This is expected because the `@..@` values remain
behind earlier unsupported `OBJECT` syntax when `ACTUAL KEY` is deferred. The
rule is retained because it has focused corpus coverage, no observed regression,
and is needed before safely retrying `ACTUAL KEY`.
