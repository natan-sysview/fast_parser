# COBOL Layout Profiles

## Purpose

Classify the physical column layout of COBOL inventory files before parsing.
The original source bytes remain unchanged. A later parse normalizer can use
these profiles to build a parser input view and a source map back to the
original file.

Column numbers in profile names are human COBOL columns, starting at 1.
Implementation code may slice with 0-based byte offsets, but reports and
profile names should stay human-readable.

## Primary Production Family

The main family to optimize first is normal fixed COBOL:

- Column 1-6: sequence prefix or blank prefix.
- Column 7: indicator.
- Column 8-72: source area.
- Column 73-80: optional suffix/identification area.

This is the family behind names containing:

```text
7_INDICATOR_8_72_SOURCE
```

When users say "columns 7 to 72", verify whether they mean the COBOL indicator
plus source window, or the source window itself. In classic COBOL, source text
normally starts at human column 8.

## Profile Names

| Layout profile | Meaning |
| --- | --- |
| `FIXED_1_6_SEQUENCE_7_INDICATOR_8_72_SOURCE` | Fixed source. Columns 1-6 contain sequence data, column 7 is the indicator, columns 8-72 are source. |
| `FIXED_1_6_SEQUENCE_7_INDICATOR_8_72_SOURCE_73_80_SUFFIX` | Same fixed source window, with consistent suffix data in columns 73-80. |
| `FIXED_1_6_BLANK_7_INDICATOR_8_72_SOURCE` | Fixed source. Columns 1-6 are mostly blank, column 7 is the indicator, columns 8-72 are source. |
| `FIXED_1_6_BLANK_7_INDICATOR_8_72_SOURCE_73_80_SUFFIX` | Same blank-prefix fixed source window, with consistent suffix data in columns 73-80. |
| `FIXED_1_6_SEQUENCE_7_INDICATOR_8_66_SOURCE_67_80_SUFFIX` | Short fixed source. Columns 8-66 are source and 67-80 behave like suffix data. |
| `FIXED_1_6_BLANK_7_INDICATOR_8_66_SOURCE_67_80_SUFFIX` | Short fixed source with blank prefix. |
| `SHIFTED_1_6_BLANK_7_72_SOURCE` | Nonstandard shifted source: columns 1-6 are blank and source appears to start at column 7. |
| `FREE_1_N_SOURCE` | Free source form from column 1 through the real line end. |
| `MIXED_COLUMNS` | Strong evidence from more than one layout family. Use for diagnostics before normalization. |
| `UNKNOWN_COLUMNS` | Not enough evidence to classify safely. |
| `BINARY_OR_CONTROL_BYTES` | Input has binary/control bytes that should be treated as an input-quality issue. |
| `EMPTY_FILE` | No nonblank source content was found in the scanned window. |
| `UNREADABLE` | File could not be read from the inventory path. |

## Column Contract Fields

Each detected profile stores a column contract in the inventory:

| Field | Meaning |
| --- | --- |
| `source_form` | `FIXED`, `FIXED_SHORT`, `SHIFTED_FIXED`, `FREE`, `MIXED`, `UNKNOWN`, or an input-quality category. |
| `sequence_prefix_start_col` | Human start column for the sequence/prefix area. |
| `sequence_prefix_end_col` | Human end column for the sequence/prefix area. |
| `indicator_col` | Human indicator column, normally 7 for fixed COBOL. |
| `source_start_col` | Human start column for parser source input. |
| `source_end_col` | Human end column for parser source input, or null for `N`. |
| `suffix_start_col` | Human start column for ignored suffix data. |
| `suffix_end_col` | Human end column for ignored suffix data. |

## Parser Input Normalization

The experimental parser normalizer uses a preserve-column strategy for normal
fixed COBOL. It does not move source text to column 1.

For profiles with:

```text
7_INDICATOR_8_72_SOURCE
```

the parser input view keeps column 7 and columns 8-72 in their original
positions. It trims columns after 72 for normal fixed profiles. Columns 1-6
are blanked for fixed profiles before parsing, regardless of whether the
detector described them as mostly sequence or mostly blank; rare nonblank
values in that prefix area are physical layout/control text, not COBOL source.

For `FIXED_SHORT` profiles, the parser input view blanks columns 1-6 but does
not trim after the detected short source end. Carlos `PCOMIS01.cbl` showed real
COBOL source after column 66, so short fixed detection is treated as a hint for
prefix handling rather than a safe suffix-cut contract.

Tabs in fixed-profile input are expanded to spaces before column blanking. This
keeps copybook data entries with tabbed indentation parseable without changing
the original source bytes.

This means Tree-sitter still sees fixed-format columns:

```text
cols 1-6   prefix area, blanked for fixed/fixed-short profiles
col 7      original indicator
cols 8-72  original source area
cols 73-N  removed from parser input for normal fixed profiles
```

## Detection Scope

The detector is conservative. It is meant to guide validation batches and parse
normalization experiments, not to replace source ownership metadata or dialect
profiles.

Default subtypes:

```text
PROGRAM
SQL_COBOL
COPYBOOK
UNKNOWN
```

JCL is intentionally excluded by default.
