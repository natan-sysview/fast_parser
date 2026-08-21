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

```cobol
     IF W-SIG-TRABAJO GREATER 20 OR LESS 19
        CONTINUE
     END-IF.
```

```cobol
     IF CTA-CHQ NOT= CTA-CHQ-ANT
        CONTINUE
     END-IF.
```

```cobol
     IF RGEC030-DIAS GREATER THAN CTE-30 AND LESS OR EQUAL
        TO CTE-90
        CONTINUE
     END-IF.
```

```cobol
     IF WS-VALUE < WS-MIN OR
                        > WS-MAX
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

The 2026-08-14 follow-up also accepts:

```text
(AND | OR) GREATER <comparison-operand>
(AND | OR) LESS <comparison-operand>
(AND | OR) LESS OR EQUAL [TO] <comparison-operand>
(AND | OR) GREATER OR EQUAL [TO] <comparison-operand>
NOT=<comparison-operand>
```

This is intentionally narrower than a generic expression fallback.

The 2026-08-14 linebreak-operator follow-up also accepts newline between
`AND`/`OR` and abbreviated `<`/`>` operators when the operator is indented
on the continuation line:

```text
(AND | OR) <newline> <horizontal-space>+ (< | >) <comparison-operand>
```

This intentionally excludes free-form source markers such as `>` in column 1.

## Corpus Examples

- `abbreviated not equal continuation`
- `abbreviated equality after line-broken or`
- `abbreviated less greater without than`
- `compact not equal operator`
- `abbreviated less or equal split to`
- `abbreviated operator after line-broken or`
- `abbreviated operator after line-broken and`
- `line-broken and followed by source marker`

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

## 2026-08-14 Safe Tail Follow-Up

Validated against the COBOL inventory of 74,242 files after the `EXEC CICS` reference-modification repair.

- `tree-sitter generate`: passed.
- `tree-sitter test`: 194/194 passed.
- FastParse extension build target `fastparse_language_cobol`: passed.
- Parsed OK: 74,242.
- Hard failures: 0.
- Files with `ERROR`: 2,426 before, 2,336 after.
- `ERROR` nodes: 3,062 before, 2,971 after.
- Files with `MISSING`: 2 before, 2 after.
- `MISSING` nodes: 2 before, 2 after.
- Changed files: 90 improved, 0 regressed.

An attempted broader form, `(AND | OR) <comparison-operand>`, was rejected in this batch. It improved some bare literal chains but regressed normal boolean conditions: 97 files improved and 106 regressed in the broad candidate. The stable v2 keeps only comparator-bearing abbreviated tails and compact `NOT=`.

Artifacts:

- Report: `runs/cobol_abbreviated_comparison_continuation_repair_report.md`.
- Validation DB: `runs/candidate_compare_current_abbreviated_comparison_continuation_full.sqlite`.
- Repair audit: `audits/abbreviated_comparison_continuation_repair/`.
- Profile report: `runs/cobol_abbreviated_comparison_continuation_profile_validation_summary_report.md`.
- 2026-08-14 safe-tail report: `runs/cobol_abbreviated_comparison_safe_tails_v2_repair_report.md`.
- 2026-08-14 safe-tail validation DB: `runs/candidate_compare_current_abbreviated_comparison_safe_tails_v2_20260814.sqlite`.
- 2026-08-14 safe-tail audit: `audits/abbreviated_comparison_safe_tails_v2_20260814/`.
- 2026-08-14 discarded broad candidate audit: `audits/abbreviated_comparison_dialect_tails_20260814_candidate/`.

## 2026-08-14 Linebreak Operator v2 Follow-Up

Validated against the COBOL inventory of 74,242 files after the
`orphan_end_exec_statement` repair.

- `tree-sitter generate`: passed.
- `tree-sitter test`: 200/200 passed.
- FastParse extension build target `fastparse_language_cobol`: passed.
- Parsed OK: 74,242.
- Hard failures: 0.
- Files with `ERROR`: 2,334 before, 2,312 after.
- `ERROR` nodes: 2,969 before, 2,944 after.
- Files with `MISSING`: 0 before, 0 after.
- `MISSING` nodes: 0 before, 0 after.
- Changed files: 25 improved, 0 regressed.

The first linebreak-operator candidate was rejected because it allowed a bare
newline before `<`/`>`, which misread `>` in column 1 as a comparison operator
in `FREE_1_N_SOURCE` programs. The stable v2 requires horizontal indentation
before a line-broken `<` or `>` operator.

Artifacts:

- 2026-08-14 linebreak v2 report: `runs/cobol_abbreviated_comparison_linebreak_operators_v2_repair_report.md`.
- 2026-08-14 linebreak v2 validation DB: `runs/candidate_compare_current_abbreviated_comparison_linebreak_operators_v2_20260814.sqlite`.
- 2026-08-14 linebreak v2 audit: `audits/abbreviated_comparison_linebreak_operators_v2_20260814/`.
- 2026-08-14 rejected linebreak v1 audit: `audits/abbreviated_comparison_linebreak_operators_20260814/`.
