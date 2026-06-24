# FastParse Public Contracts

This document defines the behavior that applications, bindings, and AI coding agents can rely on when integrating FastParse.

Contract status labels:

- `Stable`: intended to remain compatible within the `0.1.x` release line.
- `Preview`: usable, but may change before the first stable `0.1.0` contract is finalized.
- `Internal`: implementation detail; callers must not depend on it.

## Core Boundary

Status: `Stable`

FastParse is a memory-only parsing library.

The parent application owns:

- Reading files, streams, databases, or network sources.
- Walking directories and projects.
- Choosing worker/thread counts.
- Creating queues, pools, and schedulers.
- Creating databases or writing files.
- Persisting results.
- Logging, progress reporting, retries, and cancellation policy.
- Mapping AST nodes into domain objects.

FastParse owns:

- Parsing one source buffer already present in memory.
- Traversing the Tree-sitter AST.
- Filtering nodes by grammar rule name.
- Filtering node fields by bit mask.
- Serializing the requested output into memory.

FastParse must not read source files from disk, write outputs to disk, create databases, or own application-level thread pools.

## Input Contract

Status: `Stable`

Native input:

```text
source: const unsigned char *
source_len: size_t
language: string
options: parse options
```

Rules:

- `source` points to immutable bytes.
- `source_len` is the exact byte length of `source`.
- The source buffer must remain valid until `fastparse_parse` returns.
- FastParse does not mutate `source`.
- FastParse does not retain `source` after `fastparse_parse` returns.
- FastParse does not require UTF-8 input to parse.
- Byte offsets are based on the exact input bytes.
- Text fields are slices of the original source bytes serialized according to the chosen output format.

The parent language decides how to decode filenames, file contents, streams, or database values before passing bytes to FastParse.

## Language Contract

Status: `Stable` for `java`; `Preview` for future languages.

Current supported language name:

```text
java
```

Rules:

- `NULL`, empty, or omitted language means `java` in the current preview line.
- Language names are lowercase.
- Unsupported language names return a controlled error.
- Future languages must use stable lowercase names, for example `csharp`, `rust`, `python`, or `javascript`.

## Language Extension Loading Contract

Status: `Preview`

The core can load optional parse languages from native language extension libraries.

Official grammar extensions must also follow [FastParse Grammar Standard](grammar_standard.md).

Native functions:

```text
fastparse_load_language_extension
fastparse_language_available
fastparse_language_load_result_free
```

Rules:

- Java remains built into the core package.
- Extensions are native dynamic libraries with a `fastparse_language_extension_descriptor` symbol.
- A successfully loaded extension registers one canonical language name, for example `cobol`.
- Parent applications should load extensions during setup, before starting concurrent parse workers.
- Loading an extension does not parse source code and does not read application source files.
- Unsupported or unloaded language names return `TSMP_ERROR_UNSUPPORTED_LANGUAGE` from parse calls.
- Failed extension loads return `TSMP_ERROR_EXTENSION_LOAD` with a diagnostic message when available.

The current preview supports explicit path loading. Package-manager bundled discovery is planned separately.

Example flow:

```text
load extension path -> verify language_available("cobol") -> parse source bytes with language="cobol"
```

## Rule Filter Contract

Status: `Stable`

`include_rules` is a pipe-separated exact-match list of Tree-sitter grammar rule names:

```text
class_declaration|method_declaration|field_declaration
```

Rules:

- `NULL` means all named AST nodes.
- Empty string means all named AST nodes.
- Matching is exact and case-sensitive.
- Output order is AST traversal/source order.
- No matches is a valid successful result with `node_count = 0`.
- Anonymous tokens are not included as top-level nodes.

Production callers should request only the rules they need once they know the target grammar.

## Field Filter Contract

Status: `Stable` for field names and meanings; `Preview` for detailed `children` shape.

`fields = 0` means the exploratory/default field set.

Available field flags:

```text
TSMP_FIELD_ID
TSMP_FIELD_PARENT_ID
TSMP_FIELD_RULE
TSMP_FIELD_TEXT
TSMP_FIELD_RANGE
TSMP_FIELD_BYTE_RANGE
TSMP_FIELD_CHILD_COUNT
TSMP_FIELD_CHILDREN
TSMP_FIELD_DIAGNOSTICS
TSMP_FIELD_ALL
```

Stable logical fields:

```text
id
parentId
rule
text
startLine
startColumn
endLine
endColumn
startByte
endByte
childCount
children
hasErrors
errorNodeCount
missingNodeCount
errorByteCount
isError
isMissing
hasError
```

Rules:

- If a field is not requested, it should not appear in JSON/Binary output.
- CSV includes only flat requested fields.
- `text` is the original source slice for the node.
- `rule` is the Tree-sitter grammar rule name.
- `id` is unique inside one parse result.
- `parentId` points to the parent node id when available, otherwise it is null/empty according to format.
- `childCount` is the number of direct Tree-sitter children.
- `children` is intended for exploration and may be refined before stable `0.1.0`.
- Diagnostic fields are emitted only when `TSMP_FIELD_DIAGNOSTICS` is requested, or when the default/all field set is used.

Production callers should request only fields they need. Development and exploration tools may request all fields.

## Position Contract

Status: `Stable`

Line, column, and byte positions are part of the public contract because they are required for UI highlighting, reports, IDE navigation, database inventories, and automated findings.

Position fields:

```text
startLine
startColumn
endLine
endColumn
startByte
endByte
```

Rules:

- `startLine` and `endLine` are 1-based.
- `startColumn` and `endColumn` are 0-based.
- `startByte` and `endByte` are 0-based byte offsets.
- `endByte` is exclusive.
- Byte offsets are measured over the original input bytes.
- Line and column values are reported from Tree-sitter points.
- Columns are byte-oriented Tree-sitter columns, not Unicode grapheme counts.

Example:

```json
{
  "rule": "method_declaration",
  "text": "void run() {}",
  "startLine": 2,
  "startColumn": 2,
  "endLine": 2,
  "endColumn": 15,
  "startByte": 15,
  "endByte": 28
}
```

## Diagnostics Contract

Status: `Stable` for field names and meanings; `Preview` for future diagnostic detail expansion.

Tree-sitter can recover from invalid, incomplete, or unsupported syntax. FastParse exposes that recovery information instead of treating every grammar problem as a hard parse failure.

Request diagnostics with:

```text
TSMP_FIELD_DIAGNOSTICS
```

Top-level diagnostic fields:

```text
hasErrors
errorNodeCount
missingNodeCount
errorByteCount
```

Per-node diagnostic fields:

```text
isError
isMissing
hasError
```

Meanings:

- `hasErrors` means Tree-sitter reported an `ERROR` or `MISSING` node anywhere in the full parse tree.
- `errorNodeCount` is the number of Tree-sitter `ERROR` nodes in the full parse tree.
- `missingNodeCount` is the number of Tree-sitter `MISSING` nodes in the full parse tree.
- `errorByteCount` is the total byte span covered by `ERROR` nodes.
- `isError` means this node itself is an `ERROR` node.
- `isMissing` means this node itself is a `MISSING` node.
- `hasError` means this node or one of its descendants contains a parse error.

Rules:

- Diagnostics are grammar quality signals, not native call failures.
- A parse can return `TSMP_OK` and still report `hasErrors = true`.
- Diagnostics are computed from the full Tree-sitter tree, even when `include_rules` filters the returned node list.
- JSON and Binary include top-level diagnostics when requested.
- JSON, CSV, and Binary include per-node diagnostics when requested.
- Stats currently returns counts only and does not return a diagnostics payload.
- Bindings should expose diagnostics as ordinary output fields, not as exceptions.

Recommended uses:

- Evaluating grammar coverage across large corpora.
- Detecting where a language extension needs improvement.
- Supporting newer language syntax before the grammar fully understands it.
- Letting parent applications store parse quality metrics next to extracted rules.

## Output Format Contract

Status: `Stable` for format names and high-level behavior.

Supported formats:

```text
JSON
CSV
Binary
Stats
Diagnostics
```

### JSON

Status: `Stable`

JSON is intended for exploration, debugging, tools, and AI-assisted integrations.

Rules:

- Output is valid UTF-8 JSON.
- Output contains document metadata and a `nodes` array.
- Requested fields control node object contents.
- Text is escaped so the JSON document remains valid.
- Non-UTF-8 source bytes are represented safely according to the JSON renderer.

### CSV

Status: `Stable`

CSV is intended for inventories, spreadsheets, and tabular pipelines.

Rules:

- Output includes a header row.
- Output includes one row per matched node.
- Output is flat.
- Complex nested `children` data is not a CSV contract.

### Binary

Status: `Stable` for MessagePack container and `schemaVersion`; `Preview` for adding optional fields.

Binary is intended for high-performance bindings and applications.

Rules:

- Output is MessagePack bytes.
- Output includes a binary schema version.
- Output does not convert the full result into JSON text.
- Parent languages decode the MessagePack payload into their own native structures.
- New optional fields may be added in future schema-compatible releases.
- Breaking binary schema changes require a schema version change.

### Stats

Status: `Stable`

Stats is intended for counting, probing, and benchmarks.

Rules:

- Stats does not return an output payload.
- `data = NULL`.
- `length = 0`.
- `node_count` is populated.

### Diagnostics

Status: `Preview`

Diagnostics is intended for ultra-light grammar quality evaluation.

Rules:

- Output is a small UTF-8 JSON object.
- Output does not include AST nodes.
- Output does not include source text.
- Output ignores field selection.
- `node_count` is the full named node count.
- Top-level diagnostic counters are computed from the full Tree-sitter tree.
- This format is preferred for scanning large corpora before requesting full AST output from selected files.

## Result Memory Contract

Status: `Stable`

Native result shape:

```c
typedef struct {
    int status;
    unsigned char *data;
    size_t length;
    size_t node_count;
    char *error_message;
} TsmpResult;
```

Rules:

- FastParse allocates result memory.
- The caller/binding must call `fastparse_result_free`.
- Each result must be freed exactly once.
- `data` is owned by FastParse until `fastparse_result_free`.
- `error_message` is owned by FastParse until `fastparse_result_free`.
- Bindings should copy `data` into runtime-owned memory before freeing the result.
- `source` memory remains owned by the caller.
- FastParse does not retain pointers to `source`, `options`, or `result` after returning.

## C ABI Contract

Status: `Stable`

New integrations should use:

```text
fastparse_version
fastparse_parse
fastparse_result_free
```

Compatibility aliases:

```text
tsmp_version
tsmp_parse
tsmp_result_free
```

Rules:

- Compatibility aliases exist for older internal users.
- New bindings should prefer `fastparse_*` symbols.
- Struct layout, function names, and format/field constants are part of the public ABI contract.

## Concurrency Contract

Status: `Stable`

FastParse is thread-safe per parse call.

The core promise:

```text
Multiple threads may call fastparse_parse at the same time.
```

Safe:

- Many threads parsing different immutable source buffers.
- Many threads parsing the same immutable source buffer.
- One independent result object per active call.
- Freeing independent results in parallel.
- Parent runtimes using their own thread pools, queues, and worker scheduling.
- Loading all required language extensions before worker threads begin.

Not safe:

- Mutating a source buffer while FastParse is parsing it.
- Reusing one mutable `TsmpResult` for multiple active calls.
- Reading a result while another thread frees the same result.
- Freeing the same result more than once.
- Sharing mutable binding state without synchronization.
- Loading new language extensions while other threads are actively parsing.

Rules:

- `fastparse_parse` must not rely on per-call mutable global state.
- Each parse call owns its parser/context/result memory for that call.
- FastParse does not create application worker threads.
- FastParse does not own caller locks, queues, pools, or database coordination.
- Completion order across threads is unspecified.

Binding guidance:

- C callers should allocate one result object per call.
- C# callers should prefer one `FastParseClient` per worker for simple high-throughput code.
- Python callers may use threads, but should keep SQLite/file writes coordinated by the parent application.
- Rust and Java bindings should expose thread-safe call patterns without hiding application-level scheduling.

Example parent-application flow:

```text
read source bytes -> enqueue work -> worker calls FastParse -> copy result -> free result -> parent stores/uses data
```

## Normalization Contract

Status: `Preview`

FastParse can apply memory-only source normalization before parsing. Normalization is intended for legacy source files that contain transport/editor markers that are not part of the program text.

Supported native modes:

```text
TSMP_NORMALIZATION_AUTO_SAFE
TSMP_NORMALIZATION_NONE
TSMP_NORMALIZATION_COBOL_FIXED_LEGACY
```

Binding names:

```text
auto_safe
none
cobol_fixed_legacy
```

Default binding behavior:

- Python: `normalization="auto_safe"`.
- C#: `ParseOptions.Normalization = FastParseNormalization.AutoSafe`.
- C ABI V2: caller chooses `TsmpOptionsV2.normalization`.
- C ABI compatibility parse: `fastparse_parse` / `tsmp_parse` behaves as `TSMP_NORMALIZATION_NONE`.

Current `auto_safe` behavior:

- For `language = "cobol"`, applies `cobol_fixed_legacy`.
- For modern languages such as Java, leaves bytes unchanged.

Current COBOL fixed legacy cleanup:

- Removes UTF-8 BOM at the start.
- Removes final legacy EOF/control markers: `0x1A`, `0x7F`, and NUL.
- Removes final invalid trailer records `FHA` and a lone `*` in column 1.
- Does not shift COBOL columns.
- Does not remove valid fixed-format code records.
- Does not write normalized source to disk.

Output contract:

- AST fields are still controlled by the normal output field mask.
- Normalization changes the bytes that Tree-sitter sees, so `text`, byte ranges, and line/column positions are relative to the normalized in-memory source.
- Use `none` when byte-for-byte original offsets are required.

## Error Contract

Status: `Preview`

Rules:

- Non-zero native status means the parse failed.
- `error_message` should describe the failure when available.
- Unsupported language names return a controlled error.
- Bindings should surface native errors as language-native exceptions or error values.

Detailed numeric error codes are still preview and may be refined before stable `0.1.0`.

## Stability Summary

Stable for the `0.1.x` line:

- Memory-only input/output boundary.
- Java language name: `java`.
- Exact-match `include_rules`.
- Field bitmask model.
- Position fields and base rules.
- JSON, CSV, Binary, and Stats format names.
- MessagePack binary format with schema versioning.
- Result memory ownership and `fastparse_result_free`.
- C ABI function names and struct shape.
- Thread-safe per-call concurrency model.

Preview:

- Exact shape of `children`.
- Detailed numeric error codes.
- Future language names and grammar coverage.
- Additional optional fields in Binary output.
- Additional optional diagnostic metrics.
- `pretty` formatting behavior.

Internal:

- Tree-sitter parser allocation strategy.
- Internal buffers.
- Traversal implementation details.
- Build system layout.
- Benchmark numbers.
