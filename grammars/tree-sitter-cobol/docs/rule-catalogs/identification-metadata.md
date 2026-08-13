# Rule Catalog: Identification Metadata

Status: implemented in experimental grammar; binary validation pending more disk space.

## Goal

Parse COBOL identification metadata paragraphs even when their descriptive text is absent.

Many enterprise programs contain paragraphs such as `DATE-COMPILED.` or `SECURITY.` with no text before the next division. Requiring at least one `comment_entry` causes recovery errors around `ENVIRONMENT DIVISION` and later headers.

## Intended Nodes

Existing nodes are reused:

- `author_section`
- `installation_section`
- `date_written_section`
- `date_compiled_section`
- `security_section`

## Accepted Forms

```cobol
       DATE-COMPILED.
       ENVIRONMENT DIVISION.
```

```cobol
       SECURITY.
       DATA DIVISION.
```

```cobol
       AUTHOR. JOHN DOE.
```

## Excluded From First Batch

- Full semantic validation of metadata text.
- Rewriting the external `comment_entry` scanner.
- Changing division ordering.

## Baseline Metrics To Beat

After the `VALUE` clause repair:

- Files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- `ERROR` nodes: 79,778.
- `MISSING` nodes: 2,339.
- `DIVISION_SECTION_HEADER` family: 23,955 `ERROR` nodes.
- `PROCEDURE_PARAGRAPH` family: 11,731 `ERROR` nodes.

## Success Criteria

- `tree-sitter generate` succeeds.
- Corpus examples for empty metadata paragraphs pass.
- Full inventory diagnostics has zero hard failures.
- Net `ERROR` count does not increase.
- Regression set is saved and inspected before promotion.

## Validation Result

Validated on 2026-06-25 with compact full-inventory diagnostics over 74,151 non-JCL COBOL files.

- Parsed OK: 74,151.
- Hard failures: 0.
- Files improved: 19,765.
- Files regressed: 9.
- Files became clean: 6,503.
- Files became dirty: 0.
- `ERROR` nodes: 79,778 before, 59,646 after.
- `MISSING` nodes: 2,339 before, 2,334 after.
- Compact diagnostics SQLite integrity check: `ok`.

Full binary MessagePack validation was attempted twice but blocked by available disk space. The failed partial DBs were removed because they were incomplete.

## Artifacts

- Diagnostics DB: `runs/candidate_compare_current_identification_metadata_full.sqlite`.
- Report: `runs/cobol_identification_metadata_repair_report.md`.
- Comparison audit: `audits/identification_metadata_repair/`.
