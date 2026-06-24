# FastParse Python Language Extension

Status: `Preview`

This extension registers the canonical parse language:

```text
python
```

It uses the vendored `grammars/tree-sitter-python` grammar and exports:

```text
fastparse_language_extension_descriptor
tree_sitter_python
```

Build locally:

```bash
cmake -S . -B build-python-extension -DCMAKE_BUILD_TYPE=Release \
  -DFASTPARSE_PYTHON_GRAMMAR_DIR=grammars/tree-sitter-python
cmake --build build-python-extension --config Release --target fastparse_language_python
```

Load explicitly:

```python
from fastparse import FastParse

parser = FastParse()
parser.load_language_extension("bin/libfastparse_language_python.dylib")
result = parser.parse_text("def run():\n    return 1\n", language="python")
```

The packaged-extension goal is:

```python
parser.load_bundled_language("python")
```
