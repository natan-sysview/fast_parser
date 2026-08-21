# multiline-string-newline-boundary

## Purpose

Correct fixed-format COBOL multiline string scanning so an unterminated literal stops at the physical line break and then uses the continuation-line rule.

## Included Forms

- `DISPLAY "` followed by a continuation line like `      -    "                " AT 2105`.
- Continued strings where the continuation quote is followed by visible text and a closing quote before `AT`.

## Excluded Forms

- No free-form string concatenation changes.
- No change to quote escaping or non-continued single-line literals.
- No grammar-level recovery for malformed literals without a fixed-format continuation indicator.

## Local Shape

```cobol
           DISPLAY "
      -    "                " AT 2105 WITH HIGHLIGHT.
```

## Corpus

- `display_tolerances.txt`: `display empty first line continued string`.
- `display_tolerances.txt`: `display continued string with text after continuation quote`.

## Audit Notes

The previous scanner loop allowed `multiline_string` to pass through `\\r`/`\\n` while looking for a closing quote. In CRLF fixed-format sources, this made the quote in column 12 of the continuation line close the original literal too early and caused the remaining display screen code to be parsed as unrelated tokens.

## Validation

- Baseline: `baselines/before_cementera_multiline_string_newline_fix_20260821/`.
- Corpus: `tree-sitter test` passed 263/263.
- Cementera validation DB: `runs/candidate_compare_current_cementera_multiline_string_newline_fix_20260821.sqlite`.
- Before: 4,169 files, 342 `ERROR` nodes, 3 `MISSING` nodes.
- After: 4,169 files, 291 `ERROR` nodes, 3 `MISSING` nodes.
- Delta: 50 improved files, 0 regressed files, net -51 `ERROR` nodes.
