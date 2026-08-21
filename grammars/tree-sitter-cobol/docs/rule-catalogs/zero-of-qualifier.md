# zero-of-qualifier

## Purpose

Accept `0F` as a legacy typo for `OF` inside qualified data names.

## Basis

Cementera contains:

```cobol
MOVE CDACESSO  0F DPREV006 TO WS-CDACESSO-G
CDACESSO  0F DPREV006 NOT EQUAL WS-CDACESSO-G
```

The `0F` text is a zero followed by `F`, but syntactically it is intended to be the COBOL qualifier separator `OF`.

## Included Forms

- `<word> 0F <word>` wherever `qualified_word` accepts `OF`.

## Excluded Forms

- Treating `0F` as a general keyword outside `_in_of`.
- Accepting other misspellings of `OF`.

## Grammar Shape

Adds hidden token `_ZERO_OF` and includes it in `_in_of`.

## Corpus

- `hyphenated_data_names.txt`
  - `qualified name with zero-of typo`

## Audit Result

Full Cementera validation `runs/candidate_compare_current_cementera_zero_of_qualifier_20260821.sqlite` reduced total `ERROR` nodes from 167 to 166 and files with `ERROR` from 192 to 191, with zero `MISSING` nodes before and after. Improved file:

- `PCONVMSG.sqlcbli`

No regressions were found.
