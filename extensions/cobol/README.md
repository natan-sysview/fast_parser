# FastParse COBOL Language Extension

Status: `Preview`

This extension registers the canonical FastParse parse language:

```text
cobol
```

It uses the vendored grammar at `grammars/tree-sitter-cobol` and exports:

```text
fastparse_language_extension_descriptor
tree_sitter_COBOL
```

Build locally from the vendored grammar:

```bash
cmake -S . -B build-cobol-extension -DCMAKE_BUILD_TYPE=Release \
  -DFASTPARSE_COBOL_GRAMMAR_DIR=grammars/tree-sitter-cobol
cmake --build build-cobol-extension --config Release --target fastparse_language_cobol
```

Package a local native archive:

```bash
python3 scripts/package_language_extension.py \
  --language cobol \
  --version 0.1.0-preview.1 \
  --platform macos \
  --arch arm64
```

Load explicitly:

```python
from fastparse import FastParse

parser = FastParse()
parser.load_language_extension("bin/libfastparse_language_cobol.dylib")
result = parser.parse_text(cobol_source, language="cobol")
```

The grammar accepts full COBOL programs, copybook fragments, and COBOL sources with embedded `EXEC SQL ... END-EXEC` blocks. Fixed-column and legacy layout normalization is handled before parsing by FastParse or the lab validation tools.
