# Screen Section, Level 88 PIC, And Unbalanced IF Condition

## Rules

- `screen_section`
- `screen_description`
- `_condition_name_entry` with optional `picture_clause`
- `unbalanced_boolean_condition`
- `close_unbalanced_if_parentheses_before_statement`

## Purpose

Cover Cementera COBOL forms that appeared after the previous parser improvements:

- Minimal `SCREEN SECTION` data entries.
- Legacy condition-name entries such as `88 RESP-S PIC X VALUE "S"`.
- `IF` conditions where a boolean branch contains an unclosed parenthesized expression before a statement.
- Parser-input normalization that closes missing IF condition parentheses before the first following statement.

## Included Forms

```cobol
SCREEN SECTION.
01 TEL-MENU.
   02 BLANK SCREEN.
   02 LINE 05 COLUMN 01 VALUE "[1-Cria]".
   02 LINE 10 COLUMN 01 VALUE "[ ] Opcao" BLINK.
```

```cobol
88 RESP-S PIC X VALUE "S".
```

```cobol
IF CDSTAT OF DESTO02403 NOT = 'A' OR
   (WS-DATA1 > DATEST OF DESTO02403
   GO 075-READ-DESTO02403.
```

## Excluded Forms

- Full semantic validation of screen layouts.
- Arbitrary screen clauses not present in the initial Cementera examples.
- Source rewrites; missing parentheses are added only to parser input.
- Arithmetic `COMPUTE` expressions with omitted parentheses remain handled by `unbalanced_compute_expr`.

## Corpus

```text
condition_name_value_list.txt
condition_parenthesized_value_list.txt
screen_section.txt
```

Corpus result:

```text
Total parses: 299
Successful parses: 299
Failed parses: 0
```

## Cementera Validation

Baseline:

```text
runs/candidate_compare_current_cementera_display_at_suffix_period_shift_20260821.sqlite
```

Candidate:

```text
runs/candidate_compare_current_cementera_screen_level88_unbalanced_bool_closed_if_20260821.sqlite
```

Result:

```text
Files: 4169
Parsed OK: 4169
Hard failures: 0
Files with ERROR: 10
ERROR nodes: 4
Files with MISSING: 0
MISSING nodes: 0
```

Improved files:

```text
PGRID001.sqlcbli
PPALETVDA3.rqlcbli
TESTE.sqlcbli partially reduced error span
```

Regressions:

```text
0
```

Audit:

```text
audits/cementera_screen_level88_unbalanced_bool_closed_if_20260821/issue_nodes.sqlite
audits/cementera_screen_level88_unbalanced_bool_closed_if_20260821/error_families/
```

Decision:

```text
Stable for Cementera. Continue with the remaining four visible ERROR nodes.
```
