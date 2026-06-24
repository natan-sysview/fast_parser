# FastParse Rust Language Extension

Preview Rust language extension for FastParse.

This extension registers:

```text
language: rust
display : Rust
symbol  : tree_sitter_rust
```

Build locally:

```bash
python3 scripts/package_language_extension.py --language rust --version 0.1.0-preview.1
```

Load by explicit path:

```python
from fastparse import FastParse

parser = FastParse()
parser.load_language_extension("bin/libfastparse_language_rust.dylib")
result = parser.parse_text(
    "fn hello() { println!(\"hi\"); }",
    language="rust",
    output_format="json",
    include_rules=["function_item"],
)
print(result.text)
```

This package is a second extension-standard pilot. It is not published to PyPI, NuGet, or crates.io yet.
