# FastParse Java Faces Frontend Extension

Native FastParse extension for the grammar under
`grammars/tree-sitter-java-faces-frontend`.

- Canonical language: `java-faces-frontend`
- Display name: `Java Faces Frontend`
- Tree-sitter symbol: `tree_sitter_java_faces_frontend`
- Extension ABI: 1
- FastParse C ABI: `fastparse-c-api/0.5.0`
- Binary schema: MessagePack `tsmp-binary` version 1

## Build

```sh
cmake -S . -B build-java-faces-frontend -DCMAKE_BUILD_TYPE=Release
cmake --build build-java-faces-frontend --config Release \
  --target tsmp fastparse_language_java_faces_frontend
```

## Validate

```sh
python scripts/validate_java_faces_frontend_extension.py
```

The extension must be loaded before worker threads start. Use one FastParse
client per worker. Parent applications own file/database IO; FastParse receives
source bytes in memory and returns output bytes in memory.

GitHub Actions builds and validates this extension on Linux, macOS, and
Windows. No package-manager publication is part of that workflow.
