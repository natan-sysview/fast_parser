# Start Key Continuation Validation

Date: 2026-08-22

## Fix

AutoSafe no longer inserts a synthetic period after an incomplete `START ... KEY IS NOT LESS THAN` line when the next line is the key operand in Area A.

## Baseline

Before: `baselines/before-start-key-continuation-20260822-151409`

After: `baselines/after-start-key-continuation-20260822-151856`

## Tests

```text
tree-sitter test --rebuild
Total parses: 301
successful parses: 301
failed parses: 0
```

```text
python3 -m unittest tests.test_tsmp_contract.TsmpContractTests.test_cobol_auto_safe_normalization_handles_fixed_layout_view_repairs
Ran 1 test
OK
```

## FastParse Validation

Runtime:

```text
core=/Users/natanbarronlugo/Desktop/Proyectos/fast_parser/bin/libfastparse.dylib
extension=/Users/natanbarronlugo/Desktop/Proyectos/fast_parser/bin/libfastparse_language_cobol.dylib
output=Diagnostics
normalization=AutoSafe
workers=12
```

Carlos:

```text
files=91
ok_files=91
hard_failures=0
has_errors_files=0
files_with_ERROR=0
ERROR_nodes=0
files_with_MISSING=0
MISSING_nodes=0
lines=35,381
bytes=1,365,172
seconds=0.079511
```

Cementera:

```text
files=4,146
ok_files=4,146
hard_failures=0
has_errors_files=0
files_with_ERROR=0
ERROR_nodes=0
files_with_MISSING=0
MISSING_nodes=0
lines=2,300,953
bytes=93,085,133
seconds=1.663623
```

Combined:

```text
files=4,237
ok_files=4,237
hard_failures=0
has_errors_files=0
files_with_ERROR=0
ERROR_nodes=0
files_with_MISSING=0
MISSING_nodes=0
lines=2,336,334
bytes=94,450,305
```

Decision: stable for Carlos and current Cementera inventory universe.
