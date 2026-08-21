# perform-trailing-sequence-digit

## Purpose

Tolerate a legacy physical-line artifact where a single trailing digit appears after a paragraph-call `PERFORM`.

## Basis

Three Cementera CTB programs contain the same branch pattern:

```cobol
IF OPC = 03
   PERFORM LIMPA-TELA
   PERFORM TELA-INCLUI                                      6
   GO DELECAO.
```

Nearby branches use `PERFORM TELA-INCLUI` without the trailing digit, so the final `6` behaves like sequence or line-control residue rather than a COBOL operand.

## Included Forms

- `PERFORM <procedure> <integer>` where the integer follows the optional normal `perform_option`.

## Excluded Forms

- General numeric operands after arbitrary statements.
- Changing standard `PERFORM <procedure> <n> TIMES`.
- Treating the digit as semantic input to FastParse extraction.

## Grammar Shape

Adds named node `legacy_trailing_sequence_digit` as an optional final child of `perform_statement_call_proc`.

## Corpus

- `perform.txt`
  - `perform label with trailing sequence digit`

## Audit Result

Full Cementera validation `runs/candidate_compare_current_cementera_perform_trailing_sequence_digit_20260821.sqlite` reduced total `ERROR` nodes from 178 to 173 and files with `ERROR` from 203 to 198, with zero `MISSING` nodes before and after. Improved files:

- `CTB05001.sqlcbli`
- `CTB05003.sqlcbli`
- `CTB05007.sqlcbli`
- `NUMEROCHOP.slcblil`
- `VERIFICHOP.sqlcbli`

No regressions were found.
