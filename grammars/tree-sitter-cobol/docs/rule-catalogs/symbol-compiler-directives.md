# Rule Catalog: Symbol Compiler Directives

Status: implemented in experimental grammar.

## Goal

Recognize compiler directive lines used by enterprise COBOL sources without
treating them as COBOL statements.

Residual audit examples include:

```cobol
$$SET LIST STACK MAP LINEINFO ERRORLIMIT = 500 OPTIMIZE
```

```cobol
$SET LIST STACK MAP LINEINFO ERRORLIMIT = 500 OPTIMIZE
```

```cobol
]COMP AS $S264/OBJECT/P140/07MTP003
```

## Included Forms

- `$$SET ...`
- `$SET ...`
- `]COMP ...`
- `]SAVE ...`
- Full-line fixed-format `EJECT` listing directives.
- Full-line fixed-format `SKIP1`, `SKIP2`, and `SKIP3` listing directives.

## Excluded Forms

- Other plain-word listing directives such as `TITLE` and `SPACE`.
- JCL DD names or records that merely contain `EJECT`.
- Any semantic validation of compiler options.
- Commented directives already handled by fixed-format comment rules.

## Implementation Shape

Add named `compiler_directive` as an extra token. This lets directive lines
appear before or between COBOL constructs without forcing them into
`program_definition`.

The `EJECT` form is constrained to a full fixed-format line with optional
sequence/trailing digits so an identifier or operand named `EJECT` remains
normal COBOL syntax.

## Corpus Coverage

- OBJECT-style source with `$$SET` and `$$SET LEVEL`.
- OBJECT-style source with `]COMP`, `$SET`, and `$$SET`.

## Validation Plan

- Generate parser.
- Run `tree-sitter test`.
- Rebuild FastParse COBOL extension.
- Run full inventory validation.
- Compare against `runs/candidate_compare_current_id_division_abbreviation_full.sqlite`.
- Audit newly dirty files before deciding.

## Validation Result

Validated on 2026-06-26 against the full COBOL inventory.

- Corpus: 118/118 passed.
- Inventory files: 74,151.
- Parsed OK: 74,151.
- Hard failures: 0.
- Strict files with `ERROR`: 33,092 before, 33,092 after.
- `ERROR` nodes: 35,918 before, 35,870 after.
- Files with `MISSING`: 18 before, 18 after.
- `MISSING` nodes: 18 before, 18 after.
- Files became clean by strict `ERROR`: 0.
- Files became newly dirty by strict `ERROR`: 0.
- Files with lower `ERROR` count: 29.
- Files with higher `ERROR` count: 1.
- Net error-byte span change: +35,880 bytes.

Impact is limited to `PROGRAM` rows from the OBJECT project.

Known residual:

- `P100_13MTP005` increased from 3 to 6 `ERROR` nodes, while its error-byte span decreased.
- `P111_12MTP001` and `P140_13MTP001` improved by node count but increased error-byte span after recovery moved past directive lines.
- No clean file became dirty.

## Artifacts

- Baseline before: `baselines/2026-06-26-before-symbol-compiler-directives-repair`.
- Validation DB: `runs/candidate_compare_current_symbol_compiler_directives_full.sqlite`.
- Profile report: `runs/cobol_symbol_compiler_directives_profile_validation_summary_report.md`.
- Audit CSVs: `audits/symbol_compiler_directives_repair/`.

Decision: kept as stable experimental repair for OBJECT/Tandem-style symbol directives with documented recovery tradeoffs.

## EJECT Follow-Up

On 2026-06-26 the `EJECT` directive was added as a separate repair with its own
catalog and validation evidence:

- Catalog: `docs/rule-catalogs/eject-directive.md`.
- Report: `runs/cobol_eject_directive_repair_report.md`.
- Full validation DB: `runs/candidate_compare_current_eject_directive_full.sqlite`.

## SKIP Follow-Up

On 2026-06-30 the `SKIP1`, `SKIP2`, and `SKIP3` directives were added as a
separate repair with their own catalog and validation evidence:

- Catalog: `docs/rule-catalogs/skip-directive.md`.
- Report: `runs/cobol_skip_directive_repair_report.md`.
- Full validation DB: `runs/candidate_compare_current_skip_directive_full.sqlite`.
