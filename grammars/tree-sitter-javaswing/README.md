# tree-sitter-javaswing

[![CI](https://github.com/natan-sysview/tree-sitter-javaswing/actions/workflows/ci.yml/badge.svg)](https://github.com/natan-sysview/tree-sitter-javaswing/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Tree-sitter grammar for Java Swing source code.

`tree-sitter-javaswing` is a controlled fork of `tree-sitter-java` with additive Swing/AWT nodes for frontend structure that is otherwise hidden inside generic Java syntax. It still parses Java, but exposes official Java Swing concepts such as screens, components, listeners, layout wiring, dialog APIs, table models, combo boxes, text controls, root panes, timers, workers, focus, transfer handlers, and UI-thread invocation.

## Why This Exists

Swing is a Java library, not a separate language. In real applications, though, frontend structure and backend logic live in the same Java files. A generic Java parse tree can tell you that a method call or object creation exists, but it does not tell downstream tools that the source is building a screen, wiring a listener, mutating a table model, opening a dialog, or scheduling UI-thread work.

This grammar adds named `javaswing_*` nodes when the source syntax can prove an official Swing/AWT concept locally. The goal is a useful concrete syntax tree for editor tooling, migration analysis, code intelligence, modernization, and parser-lab validation.

## Scope

Included:

- Swing/AWT screen and component declarations, creations, and fields.
- `initComponents` generated UI blocks.
- Event listener wiring and event handler methods.
- Official layout, geometry, border, root pane, viewport, split pane, tabbed pane, toolbar, menu, popup, dialog, file chooser, table, list, combo box, spinner, text, focus, action, timer, worker, and transfer-handler APIs.
- Synthetic public corpus coverage for supported parse shapes.
- Aggregate private-inventory validation metrics without private source artifacts.

Intentionally excluded:

- Client-specific GUI frameworks and subclasses.
- Third-party layout DSLs such as JGoodies `CellConstraints` and TableLayout profiles.
- Receiver-type-dependent calls such as broad `add(...)`, `setModel(...)`, `getModel()`, `setSelectedIndex(...)`, and `setResizable(...)` when local syntax cannot prove the receiver type.
- Semantic inheritance, import-aware type resolution, or symbol-table resolution.

## Quick Start

Install dependencies:

```sh
npm ci
```

Generate parser artifacts:

```sh
npm run generate
```

Run the public quality gate:

```sh
npm run ci:check
```

Parse the public showcase example:

```sh
npm run example:parse
```

Run a small AST and query-capture demo:

```sh
npm run demo
```

## Development Commands

```sh
npm run metadata:check:public
npm run generate
npm test
npm run parse:check
npm run query:check
npm run example:parse
npm run pack:check
npm run audit:check
```

The public CI runs these checks across Linux, macOS, and Windows with active Node.js versions.

## Current Validation

Latest stable validation snapshot:

- Tree-sitter corpus: `183/183` passing.
- Full Java inventory through FastParse: `3313/3313` parsed successfully.
- Hard parse failures: `0`.
- Files with Tree-sitter `ERROR`: `0`.
- `ERROR` nodes: `0`.
- `MISSING` nodes: `0`.
- Encoding-normalized inputs: `441`.

The private source inventory is not included in this repository. Public reports use aggregate metrics only and must not include private source paths, snippets, hashes, validation databases, or diagnostics.

## Queries

The grammar ships with:

- `queries/highlights.scm`
- `queries/tags.scm`
- `queries/swing.scm`

The Swing query file is intended for downstream extraction experiments. Stable domain concepts should become named grammar nodes when they can be recognized safely by syntax alone.

## Public Node Documentation

Public node and field documentation is generated from `src/node-types.json`:

```text
docs/nodes.md
```

Parser-list readiness notes are tracked in `docs/parser-list.md`.

## Examples

Synthetic public examples live under `examples/`.

They are intentionally generic and are not copied from private projects or customer source code.

Demo instructions are in `docs/demo.md`.

## Release Status

This repository is ready for public alpha validation. The first release should be published as a GitHub pre-release and, if npm credentials are available, as an npm prerelease/dist-tag.

Tag pushes run the GitHub pre-release workflow. npm publication is manual so maintainers can configure npm trusted publishing or `NPM_TOKEN` first.

The npm package badge should be added after the first package is published.

Recommended public topics:

- `tree-sitter`
- `parser`
- `grammar`
- `java`
- `swing`
- `javaswing`

Public release history is tracked in `CHANGELOG.md`, with alpha notes in `docs/releases/0.1.0-alpha.md`.

Dependency and parser-generator upgrade policy is documented in `docs/dependency-policy.md`.

## Contributing

Contribution guidelines are in `CONTRIBUTING.md`.

Please use minimized synthetic examples in issues and pull requests. Do not paste private source code, customer project names, production paths, generated diagnostics, validation databases, or inventory exports.

## Security

Security reporting guidance is in `SECURITY.md`.
