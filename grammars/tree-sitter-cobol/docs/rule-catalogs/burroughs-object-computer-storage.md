# Rule Catalog: Burroughs Object-Computer Storage Clauses

Status: implemented in experimental grammar.

## Rule Name

`object_computer_disk`

Related existing rule extended:

- `object_computer_memory`

## Purpose

Recognize narrow Burroughs/Unisys-style computer names and
`OBJECT-COMPUTER` hardware clauses observed in the local COBOL inventory
without broadening general configuration-section recovery.

## Basis

The current stable validation DB is:

`runs/candidate_compare_current_database_section_fixed_format_edited_picture_full.sqlite`

Targeted audit evidence from the current profile issue-node DB found:

- 22 issue nodes in 20 files around `OBJECT-COMPUTER` plus `DISK SIZE` or
  `MEMORY SIZE`.
- The inventory has 34 `OBJECT` project COBOL programs; all 34 currently still
  contain at least one `ERROR` node.
- A broad first attempt that allowed arbitrary multi-word computer names caused
  an IBM regression by swallowing `EJECT`, `DATA DIVISION`, and
  `WORKING-STORAGE SECTION` after `OBJECT-COMPUTER. IBM-370.`. The final rule
  therefore accepts only one-word names generally, plus the observed
  `BURROUGHS [MODEL] <word>` multi-word form.

Observed local forms include:

```cobol
       OBJECT-COMPUTER. B-6900
                         DISK   SIZE 13000000 WORDS
                         MEMORY SIZE    40000 WORDS.
```

```cobol
       OBJECT-COMPUTER. A-10 MEMORY SIZE 3 MODULES.
```

```cobol
       OBJECT-COMPUTER. B5900  DISK SIZE 7 MODULES.
```

```cobol
       OBJECT-COMPUTER. BURROUGHS MODEL A5.
```

## Included Forms

- One-word computer names after `SOURCE-COMPUTER.` and `OBJECT-COMPUTER.`
- `BURROUGHS [MODEL] <word>` names after `SOURCE-COMPUTER.` and
  `OBJECT-COMPUTER.`
- `DISK SIZE <integer> WORDS`
- `DISK SIZE <integer> MODULES`
- `MEMORY SIZE <integer> WORDS`
- `MEMORY SIZE <integer> CHARACTERS`
- `MEMORY SIZE <integer> MODULES`
- Optional `IS` before the integer size where the existing memory rule already
  allowed it.

## Excluded Forms

- Non-integer storage sizes such as `MEMORY SIZE IS WS-MEMORY WORDS` outside
  the `OBJECT-COMPUTER` paragraph.
- Arbitrary hardware clauses not observed in the current local inventory.
- Semantic validation of machine models, disk units, memory units, or actual
  compiler support.
- `ACTUAL KEY` in `SELECT` clauses. It was retested and deferred because it
  still increased total `ERROR` nodes, even after byte-span improvement.

## Grammar Shape

```text
SOURCE-COMPUTER. (<WORD> | BURROUGHS [MODEL] <WORD>) .
OBJECT-COMPUTER. (<WORD> | BURROUGHS [MODEL] <WORD>) [<object-clause>...] .
DISK SIZE [IS] <integer> (WORDS | MODULES)
MEMORY SIZE [IS] <integer> (CHARACTERS | WORDS | MODULES)
```

Public nodes:

- `object_computer_disk`
- `burroughs_computer_name`
- `object_computer_memory`
- `MODULES`

## Corpus Coverage

- `SOURCE-COMPUTER. BURROUGHS MODEL A5.`
- `OBJECT-COMPUTER. BURROUGHS MODEL A5.`
- `DISK SIZE ... WORDS` plus `MEMORY SIZE ... WORDS`.
- `MEMORY SIZE ... MODULES`.
- `DISK SIZE ... MODULES`.
- Existing `MEMORY SIZE ... WORDS`, `MEMORY SIZE ... CHARACTERS`,
  `PROGRAM COLLATING SEQUENCE`, and `SEGMENT-LIMIT` coverage remains active.

## Validation Plan

1. Preserve a before baseline.
2. Generate parser artifacts.
3. Run `tree-sitter test`.
4. Smoke parse representative `OBJECT` files.
5. Rebuild the FastParse COBOL language extension.
6. Validate the full 74,151-file COBOL inventory.
7. Compare against
   `runs/candidate_compare_current_database_section_fixed_format_edited_picture_full.sqlite`.
8. Audit all `object_computer_disk` and `MODULES` matches.
9. Accept only if total `ERROR`/`MISSING` metrics do not regress.

## Validation Result

Validated on 2026-06-30 against the 74,151-file COBOL inventory.

- `tree-sitter generate`: passed with the pre-existing ABI 14 warning.
- `tree-sitter test --overview-only`: 162/162 passed.
- FastParse native extension: rebuilt successfully.
- Validation DB:
  `runs/candidate_compare_current_burroughs_computer_at_hex_no_actual_key_full.sqlite`
- Baseline DB:
  `runs/candidate_compare_current_database_section_fixed_format_edited_picture_full.sqlite`
- Parsed OK: 74,151.
- Hard failures: 0.
- Files with `ERROR`: 10,401 -> 10,401.
- `ERROR` nodes: 11,328 -> 11,325.
- Files with `MISSING`: 1 -> 1.
- `MISSING` nodes: 1 -> 1.
- `error_byte_count`: improved by 29,840 bytes.
- Changed files: 22, all `OBJECT`/`PROGRAM`.
- Files with lower `ERROR` node count: 4.
- Files with higher `ERROR` node count: 1 (`P115_13MTP001`, +2 nodes).
- Net `ERROR` node delta: -3.
- Validation throughput: 296.6 files/sec.

Rule-node audit over the 34 `OBJECT` programs:

- `burroughs_computer_name`: 12 nodes in 6 files.
- `object_computer_disk`: 13 nodes in 13 files.
- `at_hex_literal`: 0 parse-visible nodes in the final candidate because the
  source occurrences remain behind earlier unsupported `OBJECT` syntax when
  `ACTUAL KEY` is deferred.

Artifacts:

- Audit directory: `audits/burroughs_computer_at_hex_repair/`
- Repair report: `runs/cobol_burroughs_computer_at_hex_repair_report.md`
