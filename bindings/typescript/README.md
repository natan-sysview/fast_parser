# FastParse TypeScript Binding

TypeScript/Node/Electron binding for the FastParse C ABI.

Current status:

- Loads `libfastparse.dylib`, `libfastparse.so`, or `fastparse.dll`.
- Supports JSON, CSV, Binary MessagePack, Stats, and Diagnostics.
- Supports full AST parsing, rule filtering, field filtering, normalization, and Tree-sitter queries.
- Copies native output into a Node `Buffer` and always releases native memory through `fastparse_result_free`.
- Can load language extensions by explicit path or package layout.
- Designed for Electron main process, Node CLIs, backend services, and agent tools.

## Install

Local development from the FastParse repo:

```bash
cd bindings/typescript
npm install
npm run build
FASTPARSE_LIBRARY_PATH=/Users/natanbarronlugo/Desktop/Proyectos/fast_parser/bin/libfastparse.dylib npm test
```

Future npm install shape:

```bash
npm install @natan-sysview/fastparse
npm install @natan-sysview/fastparse-language-javaswing
```

Package-manager installs should include native assets so `FASTPARSE_LIBRARY_PATH` is not needed.

## Minimal Parse

```ts
import { FastParseClient } from "@natan-sysview/fastparse";

const parser = new FastParseClient();
const result = parser.parseText("class Demo { void run() {} }");

console.log(result.nodeCount);
console.log(result.json());
```

## JavaSwing Extension

```ts
import { FastParseClient } from "@natan-sysview/fastparse";

const parser = new FastParseClient();
parser.loadBundledLanguage("javaswing");

const ast = parser.parseText(sourceCode, { language: "javaswing" }).json();
```

For local testing without an npm extension package:

```ts
parser.loadLanguageExtension(
  "/Users/natanbarronlugo/Desktop/Proyectos/fast_parser/bin/libfastparse_language_javaswing.dylib"
);
```

## Field And Rule Filtering

```ts
const result = parser.parseText(sourceCode, {
  language: "java",
  includeRules: ["method_declaration", "class_declaration"],
  fields: ["id", "parent_id", "rule", "text", "range", "byte_range"]
});
```

By default FastParse returns the complete AST and all fields.

## Binary Output

```ts
import { OutputFormat } from "@natan-sysview/fastparse";

const result = parser.parseText(sourceCode, {
  outputFormat: OutputFormat.Binary
});

const document = result.binaryDocument();
```

Binary output is MessagePack, not JSON text.

## Diagnostics

```ts
const diagnostics = parser.parseText(sourceCode, {
  outputFormat: "diagnostics",
  fields: ["diagnostics"]
}).json();
```

Diagnostics describe Tree-sitter recovery quality (`ERROR`, `MISSING`, `hasError`). They are not native failures.

## Tree-Sitter Queries

```ts
const captures = parser.queryText(
  "class Demo { void run() {} }",
  "(method_declaration name: (identifier) @method.name) @method",
  {
    fields: ["capture_name", "rule", "text", "range", "byte_range", "pattern_index"],
    maxCaptures: 100
  }
).json();
```

Queries are the recommended production path when the developer knows the grammar rules needed by the application.

## Electron Guidance

Use this binding from the Electron main process or a preload script with controlled API exposure. Avoid loading arbitrary native paths from untrusted renderer input.

Recommended flow:

1. Main process owns file IO.
2. Main process sends source bytes/text to FastParse.
3. FastParse returns JSON/CSV/Binary/Stats/Diagnostics in RAM.
4. Main process returns only the required data to the renderer.

## Threading

FastParse native parse/query calls are thread-safe per call. Use one `FastParseClient` per worker thread unless a shared client is explicitly tested for your Electron workload. Load language extensions before starting worker threads.

## Native Loading

The loader searches:

1. Constructor `libraryPath`.
2. `FASTPARSE_LIBRARY_PATH`.
3. `TSMP_LIBRARY_PATH`.
4. Package native asset folders such as `native/<rid>/` and `runtimes/<rid>/native/`.
5. Local repo folders such as `bin/`.

Language extension override:

```text
FASTPARSE_LANGUAGE_JAVASWING_PATH=/path/to/libfastparse_language_javaswing.dylib
```
