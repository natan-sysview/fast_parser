# display-grouped-positioned-items

## Purpose

Support COBOL/400 screen `DISPLAY` blocks where one positioned item is formed by multiple literal values followed by a single `AT` clause.

## Basis

Cementera screen programs contain long display blocks like:

```cobol
DISPLAY
    "                                                      "
    "Plaqueta   :                                          "
                                                  AT 0915
    "  " AT 0970 WITH REVERSE-VIDEO.
```

The previous grammar required each repeated display item to have its own `AT`, so a filler literal before a labelled literal started a recovery span.

## Included Forms

- One or more display values followed by `AT <position>`.
- Repeated positioned groups in a single `DISPLAY`.
- Optional `WITH` attributes after each positioned group.

## Excluded Forms

- General paragraph-boundary recovery after unterminated `DISPLAY`.
- Non-screen `DISPLAY ... UPON ...` forms.
- New display attributes; this rule only changes item grouping.

## Grammar Shape

Adds `_display_positioned_group`, which repeats display values before a required screen `AT` position.

## Corpus

- `display_tolerances.txt`
  - `display grouped literals before at`
- Existing display corpus remains green:
  - `display with compact screen position`
  - `display multiple positioned items`
  - `display with attributes before at`
  - `display empty first line continued string`
  - `display continued string with text after continuation quote`

## Smoke Result

Local normalized parses became clean for the three Cementera files that were exposed by the COBOL/400 file-name repair:

- `PASSIS05.sqlcbli`
- `PPREV809.sqlcbli`
- `PPREV810.sqlcbli`

Full Cementera FastParse validation is required after rebuilding the extension.
