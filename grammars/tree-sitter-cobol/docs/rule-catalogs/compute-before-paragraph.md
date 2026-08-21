# compute-before-paragraph

## Purpose

Accept legacy COBOL procedure blocks where a `COMPUTE` statement omits the terminating period immediately before the next paragraph header.

## Included Forms

- `COMPUTE <target> = <expression>` followed directly by a paragraph header.
- The preceding block may contain normal statements such as `ACCEPT ... FROM DATE YYYYMMDD`.

## Excluded Forms

- No broad recovery for arbitrary incomplete statements before a paragraph header.
- No change to `COMPUTE` expression semantics.
- No relaxation of data division syntax.

## Local Shape

```cobol
       INICIO-PROGRAMA.
           COMPUTE WDTOM = (1000000 + ANOD * 10000 + MESR * 100 + DIAR)
       010-INICIALIZACAO.
           OPEN INPUT DMOVTO.
```

## Corpus

- `procedure_tolerances.txt`: `compute without period before paragraph`.

## Audit Notes

Initial target: Cementera files whose residual `ERROR` span starts after `ACCEPT KDAT FROM DATE YYYYMMDD` and a periodless `COMPUTE` before the next paragraph.

## Validation

- Baseline: `baselines/before_cementera_compute_before_paragraph_20260821/`.
- Corpus: `tree-sitter test` passed 261/261.
- Cementera validation DB: `runs/candidate_compare_current_cementera_compute_before_paragraph_20260821.sqlite`.
- Before: 4,169 files, 389 `ERROR` nodes, 3 `MISSING` nodes.
- After: 4,169 files, 342 `ERROR` nodes, 3 `MISSING` nodes.
- Delta: 47 improved files, 0 regressed files, net -47 `ERROR` nodes.
