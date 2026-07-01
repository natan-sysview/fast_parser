# Contributing

Thanks for helping improve `tree-sitter-javaswing`.

This grammar extends Java with official Swing and AWT frontend structure. Keep changes additive and syntax-driven unless a breaking tree-shape change is intentionally planned for a major release.

## Development Flow

Install dependencies:

```sh
npm ci
```

Run the local quality gates:

```sh
npm run generate
npm test
npm run parse:check
npm run query:check
npm run pack:check
npm run audit:check
```

If parser artifacts change, include the generated `src/parser.c`, `src/grammar.json`, and `src/node-types.json` changes in the same commit as `grammar.js`.

## Grammar Rule Guidelines

- Prefer named `javaswing_*` nodes for official Swing concepts that are locally recognizable from source syntax.
- Avoid catch-all rules for broad Java method names when receiver type information is required.
- Keep client-specific subclasses, proprietary frameworks, and third-party layout DSLs out of the official grammar.
- Add positive and negative corpus tests for each grammar rule.
- Document new public nodes in generated node documentation by regenerating parser artifacts.

## Privacy

Do not contribute private source files, local paths, validation databases, production snippets, account data, or source-derived examples from private inventories.

Use synthetic, minimized examples in `test/corpus/`. Private validation results may be discussed only as aggregate metrics.

## Issues

When reporting a parse problem, include a minimal synthetic sample whenever possible. If the original code is private, reduce it to the smallest public-safe shape that reproduces the issue.
