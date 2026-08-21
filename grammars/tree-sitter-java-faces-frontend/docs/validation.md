# Validation

## Local project evidence

The grammar was hardened against a 32-file JSF/PrimeFaces project corpus:

- 7 Facelets files and 25 PrimeFaces Facelets files.
- 1,679 source lines.
- 32/32 clean parses.
- 0 `ERROR` nodes.
- 0 `MISSING` nodes.
- 0 source hash mismatches.
- 496/496 active EL markers reconciled with expression nodes.
- 0 tag or attribute family classification mismatches.

FastParse parsed the same universe through native MessagePack output with
27,227 AST nodes and 1,483 framework/EL query captures.

## Repository validation

`.github/workflows/java-faces-frontend-ci.yml` builds and tests the grammar and
FastParse extension on:

- Ubuntu
- macOS
- Windows

Each runner executes the Tree-sitter corpus, builds the FastParse core and
extension, loads the extension through the Python binding, decodes MessagePack,
checks diagnostics and required named rules, runs an audit query, and performs
concurrent parse calls.

The workflow does not publish to NuGet, PyPI, npm, or another registry.
