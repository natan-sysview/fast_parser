# Demo

The public demo is intentionally based on synthetic source code under `examples/`.

Run:

```sh
npm ci
npm run demo
```

The demo parses `examples/swing-showcase.java` and runs `queries/swing.scm` against it. This gives users a quick way to inspect both the parse tree and the Swing-oriented query captures without needing private corpus data.

Future public demo work can add a browser-based AST viewer after a WASM build is added to the release process.
