# Java Frameworks Grammar Promotion

Date: 2026-06-30

## Source

- Experimental grammar: `experimental-grammars/tree-sitter-java-frameworks`
- Formal grammar: `grammars/tree-sitter-java-frameworks`
- Promotion approval: user approved implementing points 1 through 5, including promotion to `grammars/`.

## Scope

The formal grammar copy includes grammar source, generated parser artifacts, bindings, corpus tests, docs, and queries.

The following experimental-only artifacts were intentionally not copied:

- `runs/`
- `audits/`
- `baselines/`
- `target/`
- build caches and runtime caches

## Evidence

Before promotion, the experimental grammar passed:

- `tree-sitter test`: 4/4
- `npm pack --dry-run`: OK
- `cargo test`: OK
- FastParse framework inventory validation: 2264/2264 parsed, 0 hard failures, 0 `ERROR`, 0 `MISSING`, 0 query failures

`PROMOTION_SHA256SUMS.txt` records the hashes for the key promoted grammar files and corpus/query assets.
