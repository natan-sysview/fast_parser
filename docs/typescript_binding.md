# TypeScript Binding

The TypeScript binding lets Node.js and Electron applications call FastParse through the native C ABI.

Package path in this repository:

```text
bindings/typescript
```

## Contract

The binding follows the same high-level contract as C# and Python:

```ts
FastParseClient
ParseOptions
QueryOptions
OutputFormat
Field
Normalization
ParseResult
ParseSummary
decodeBinary
```

The parent application owns file IO, database writes, queues, and worker management. FastParse receives source bytes/text in RAM and returns JSON, CSV, Binary MessagePack, Stats, or Diagnostics in RAM.

## Electron Usage

Use FastParse from the Electron main process or from a preload script. Do not let untrusted renderer code choose arbitrary native library paths.

```ts
import { FastParseClient } from "@natan-sysview/fastparse";

const parser = new FastParseClient();
const ast = parser.parseText(sourceCode, { language: "java" }).json();
```

The public npm package name should use a scope because `fastparse` is already taken on npm:

```bash
npm install @natan-sysview/fastparse
```

## Local Validation

```bash
cd /Users/natanbarronlugo/Desktop/Proyectos/fast_parser/bindings/typescript
npm install
npm run build
FASTPARSE_LIBRARY_PATH=/Users/natanbarronlugo/Desktop/Proyectos/fast_parser/bin/libfastparse.dylib npm test
```

## Local npm Package With Native Runtime

Build a local `.tgz` package that embeds the current platform native library:

```bash
cd /Users/natanbarronlugo/Desktop/Proyectos/fast_parser
python3 scripts/package_npm.py --version 0.1.0 --include-current-native
python3 scripts/validate_npm_package.py dist/npm/natan-sysview-fastparse-0.1.0.tgz
```

The validator installs the package in a clean temporary Node project, clears `FASTPARSE_LIBRARY_PATH`, and verifies:

- Java JSON parse.
- Diagnostics output.
- Binary MessagePack decode.
- Tree-sitter query captures.
- Automatic native loading from `runtimes/<rid>/native`.

## GitHub Release Package

The release workflow builds native archives on Linux, macOS arm64, macOS x64, and Windows. The `npm-package` job then stages all native libraries into one npm tarball:

```text
runtimes/linux-x64/native/libfastparse.so
runtimes/osx-arm64/native/libfastparse.dylib
runtimes/osx-x64/native/libfastparse.dylib
runtimes/win-x64/native/fastparse.dll
```

Publishing is gated by:

```text
Repository variable: NPM_PUBLISH=true
Git tag release:     v<version>
```

The npm package should be published as:

```text
@natan-sysview/fastparse
```

because the unscoped `fastparse` name is already used on npm.

## JavaSwing

When the JavaSwing extension is installed as a package:

```ts
parser.loadBundledLanguage("javaswing");
```

For local development:

```ts
parser.loadLanguageExtension(
  "/Users/natanbarronlugo/Desktop/Proyectos/fast_parser/bin/libfastparse_language_javaswing.dylib"
);
```

## Concurrency

Native parse/query calls are thread-safe per call. For Electron or Node worker threads, use one `FastParseClient` per worker. Load language extensions before starting concurrent parse work.

## Binary Output

`OutputFormat.Binary` returns MessagePack bytes. The TypeScript binding includes `decodeBinary` and `ParseResult.binaryDocument()` for schema version 1.
