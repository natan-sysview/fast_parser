# Changelog

All notable public changes to `tree-sitter-javaswing` are documented here.

This project uses semantic versioning for public releases. Alpha releases may still change node names or tree shape before a stable `1.0.0`.

## 0.1.0-alpha.1 - 2026-06-30

Initial alpha release candidate.

### Added

- Java Swing grammar fork based on `tree-sitter-java`.
- Additive `javaswing_*` nodes for official Swing and AWT frontend structure.
- Public corpus tests for screens, components, fields, initialization blocks, listeners, event handlers, layouts, borders, geometry, menus, toolbars, dialogs, file choosers, tables, lists, combo boxes, spinners, text controls, root panes, tabbed panes, split panes, scroll panes, selection models, actions, timers, workers, focus handling, transfer handlers, and UI-thread invocation.
- Query files for highlights, tags, and Swing-oriented extraction experiments.
- Public node documentation generated from `src/node-types.json`.
- CI workflow for parser generation, corpus tests, query checks, public example parsing, package dry-run, and npm audit across Linux, macOS, and Windows.
- Cross-platform Node-based smoke and query check scripts.
- Public synthetic showcase example under `examples/`.
- Public payload builder used inside the private parser lab to copy only whitelisted grammar files.

### Validation

- Tree-sitter corpus: `183/183` passing.
- Private Java inventory through FastParse: `3313/3313` parsed successfully.
- Hard parse failures: `0`.
- Files with Tree-sitter `ERROR`: `0`.
- `ERROR` nodes: `0`.
- `MISSING` nodes: `0`.
- Encoding-normalized inputs: `441`.

Private source files, paths, validation databases, and diagnostics are excluded from public release artifacts.

### Known Limits

- Client-specific GUI frameworks and subclasses are out of scope for the official grammar.
- Third-party layout DSLs are not modeled in this alpha.
- Receiver-type-dependent calls remain generic when local syntax cannot prove the receiver type.
- Semantic inheritance and symbol-table resolution are intentionally outside the grammar.
