# Rule Catalog: Abbreviated Comparison Continuation

Status: proposed repair in experimental grammar.

## Goal

Recognize COBOL abbreviated comparison continuations in conditions where the
left operand is omitted after `AND` or `OR`.

Enterprise COBOL commonly writes conditions such as:

```cobol
     IF ESTADO-ORD NOT = '01'
        AND NOT = '14'
```

and:

```cobol
     IF COMMAREA-TRANSFER-PROG = 'SOMAS58P' OR
                              = 'SOMAS59P'
```

The comparison inherits the previous subject semantically. The grammar only
needs to recognize the local syntax so recovery does not consume the rest of
the paragraph.

## Intended Nodes

No new public node is introduced. Existing condition nodes remain:

- `if_header`
- `expr`
- `AND`
- `OR`
- `eq`
- `ne`

## Accepted Forms

```cobol
     IF ESTADO-ORD NOT = '01'
        AND NOT = '14'
        CONTINUE
     END-IF.
```

```cobol
     IF COMMAREA-TRANSFER-PROG = 'SOMAS58P' OR
                              = 'SOMAS59P' OR
                              = 'SOMAS62P'
        CONTINUE
     END-IF.
```

## Excluded Forms

- Semantic expansion of omitted operands.
- Rewriting the condition into a normalized boolean tree.
- Full compiler-level condition simplification.
- Promotion to `grammars/` before full inventory validation.

## Local Syntactic Shape

The existing `_expr_compare` rule accepts a first comparison:

```text
<expr-calc> <comparator> <comparison-operand>
```

This repair allows repeated abbreviated comparison tails:

```text
(AND | OR) <comparator> <comparison-operand>
```

This is intentionally narrower than a generic expression fallback.

## Corpus Examples

- `abbreviated not equal continuation`
- `abbreviated equality after line-broken or`

## Audit Basis

After the embedded EXEC period separator repair, the 2026-06-29 residual
issue-node audit showed repeated broad errors around real conditions containing
`AND NOT =` and line-broken `OR` followed by `=`.

Examples included `SOMMC45P`, `UG7CG108`, `SOMAS07P`, `SOMAS19P`, and related
CICS/DB2 programs.

## Success Criteria

- `tree-sitter generate` succeeds.
- `tree-sitter test` passes.
- Real smoke files with abbreviated conditions improve or remain stable.
- Full FastParse inventory validation has zero hard failures.
- `ERROR` and `MISSING` totals do not regress unexplained.

## Validation Result

Validated on 2026-06-29 against the COBOL inventory of 74,151 non-JCL files.

- `tree-sitter generate`: passed.
- `tree-sitter test`: 134/134 passed.
- FastParse extension build target `fastparse_language_cobol`: passed.
- Parsed OK: 74,151.
- Hard failures: 0.
- Parser error-flag files: 12,689 before, 11,137 after.
- Strict `ERROR` files: 12,684 before, 11,132 after.
- `ERROR` nodes: 14,381 before, 12,645 after.
- Files with `MISSING`: 1 before, 1 after.
- `MISSING` nodes: 1 before, 1 after.
- Files became strict-ERROR clean: 1,552.
- Clean files that became strict-ERROR dirty: 0.
- Files with increased `MISSING`: 0.
- Diagnostic validation throughput: 1,189.4 files/sec before, 1,035.8 files/sec after.

Decision: stable experimental repair with documented performance cost. Keep in `experimental-grammars/tree-sitter-cobol` only.

Artifacts:

- Report: `runs/cobol_abbreviated_comparison_continuation_repair_report.md`.
- Validation DB: `runs/candidate_compare_current_abbreviated_comparison_continuation_full.sqlite`.
- Repair audit: `audits/abbreviated_comparison_continuation_repair/`.
- Profile report: `runs/cobol_abbreviated_comparison_continuation_profile_validation_summary_report.md`.
