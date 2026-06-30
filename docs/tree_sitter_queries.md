# Tree-sitter Query Contract

FastParse query support lets a parent application run Tree-sitter structural queries over source code in RAM.

This is a separate contract from full AST parsing:

- `parse` returns an AST or AST-derived output.
- `query` returns only Tree-sitter query matches and captures.

The parent application still owns file IO, queues, database writes, retries, and orchestration.

## C ABI

Use `fastparse_query` for new code. `tsmp_query` is the compatibility alias.

```c
int fastparse_query(
    const unsigned char *source,
    size_t source_len,
    const unsigned char *query,
    size_t query_len,
    const TsmpQueryOptions *options,
    TsmpResult *out_result);
```

`source` and `query` are both passed in RAM. FastParse parses the source, compiles the Tree-sitter query, executes it against the root node, and returns output in `TsmpResult`.

Release memory with:

```c
fastparse_result_free(&result);
```

## Query Options

```c
typedef struct {
    const char *language;
    TsmpFormat format;
    unsigned int fields;
    size_t max_matches;
    size_t max_captures;
    int include_pattern;
    int pretty;
    TsmpNormalization normalization;
} TsmpQueryOptions;
```

Fields:

- `language`: grammar name, for example `java`.
- `format`: `JSON`, `CSV`, `STATS`, or `BINARY`.
- `fields`: capture fields to include. `0` means native query defaults.
- `max_matches`: maximum matches to return. `0` means unlimited.
- `max_captures`: maximum captures to return. `0` means unlimited.
- `include_pattern`: include `patternIndex` even if the field mask does not explicitly request it.
- `pretty`: reserved for formatted JSON.
- `normalization`: same source normalization contract as parse.

Default query fields:

```text
capture name
rule
text
line/column range
byte range
pattern index
```

## Field Flags

Query supports the standard node fields plus query-specific fields:

```text
TSMP_FIELD_CAPTURE_NAME
TSMP_FIELD_PATTERN_INDEX
TSMP_FIELD_RULE
TSMP_FIELD_TEXT
TSMP_FIELD_RANGE
TSMP_FIELD_BYTE_RANGE
TSMP_FIELD_CHILD_COUNT
TSMP_FIELD_DIAGNOSTICS
```

Important note: Tree-sitter may return captures in source/range order, not the textual order in the query pattern. Consumers should use capture names rather than assuming array order.

## JSON Output

Example query:

```scheme
(method_declaration
  name: (identifier) @method.name) @method
```

Example result shape:

```json
{
  "language": "java",
  "matches": [
    {
      "patternIndex": 0,
      "captures": [
        {
          "patternIndex": 0,
          "name": "method",
          "rule": "method_declaration",
          "text": "void run() {}",
          "startLine": 1,
          "startColumn": 13,
          "endLine": 1,
          "endColumn": 26,
          "startByte": 13,
          "endByte": 26
        }
      ]
    }
  ],
  "matchCount": 1,
  "captureCount": 2
}
```

## CSV Output

CSV output is one row per capture. Header columns are controlled by the field mask.

Typical default columns:

```csv
pattern_index,capture_name,rule,text,start_line,start_column,end_line,end_column,start_byte,end_byte
```

## Binary Output

`TSMP_FORMAT_BINARY` returns MessagePack bytes, not JSON text.

Top-level shape:

```text
format = "fastparse-query-binary"
schemaVersion = 1
language
matchCount
captureCount
matches[]
  patternIndex
  captures[]
    name?
    rule?
    text?
    startLine?
    startColumn?
    endLine?
    endColumn?
    startByte?
    endByte?
```

Text is encoded as MessagePack binary bytes so callers can decide how to decode source text.

## Stats Output

`TSMP_FORMAT_STATS` does not copy output data.

Current `TsmpResult` mapping:

- `node_count`: capture count.
- `length`: match count.
- `data`: `NULL`.

Bindings expose this as `ParseSummary`:

- `NodeCount`: capture count.
- `OutputLength`: match count for query stats.

## C# Usage

Install:

```bash
dotnet add package FastParser --version 0.1.0-preview.23
```

Run a query:

```csharp
using FastParse;

var source = "class Demo { void run() {} }";
var query = "(method_declaration name: (identifier) @method.name) @method";

using var parser = new FastParseClient();

var result = parser.QueryText(
    source,
    query,
    new QueryOptions
    {
        Language = "java",
        Format = FastParseFormat.Json
    });

Console.WriteLine(result.Text);
```

Limit fields and captures:

```csharp
var result = parser.QueryText(
    source,
    "(method_declaration name: (identifier) @method.name)",
    new QueryOptions
    {
        Fields = FastParseField.CaptureName | FastParseField.Text,
        MaxCaptures = 1,
        IncludePattern = false
    });
```

## Python Usage

```python
from fastparse import FastParse, QueryOptions, Field

source = "class Demo { void run() {} }"
query = "(method_declaration name: (identifier) @method.name) @method"

client = FastParse()
result = client.query_text(source, query)
print(result.text)
```

Limit fields:

```python
result = client.query_text(
    source,
    "(method_declaration name: (identifier) @method.name)",
    QueryOptions(
        fields=Field.CAPTURE_NAME | Field.TEXT,
        max_captures=1,
        include_pattern=False,
    ),
)
```

## Error Contract

Native failures and query failures are explicit:

- `TSMP_ERROR_INVALID_ARGUMENT`: missing source/query/options/language.
- `TSMP_ERROR_UNSUPPORTED_LANGUAGE`: grammar not loaded.
- `TSMP_ERROR_PARSE_FAILED`: parser failed or grammar/runtime mismatch.
- `TSMP_ERROR_QUERY_COMPILE`: Tree-sitter query failed to compile.
- `TSMP_ERROR_QUERY_EXECUTE`: reserved for query execution failures.
- `TSMP_ERROR_UNSUPPORTED_FORMAT`: unsupported query output format.
- `TSMP_ERROR_OUT_OF_MEMORY`: allocation or render failure.

For query compile errors, the error message includes the Tree-sitter query error category and byte offset.

## Concurrency Contract

Recommended conservative contract:

- Use one parser client per worker thread.
- Load language extensions before starting concurrent workers.
- Keep source file reads and database writes outside FastParse.
- Pass source and query text in RAM.
- Treat query calls as stateless parse-and-query operations.

## Recommended Usage Pattern

Use full AST parsing during exploration. Once the developer knows the grammar patterns:

1. Move to `query`.
2. Capture only the semantic nodes needed.
3. Reduce fields to the minimum required.
4. Use `STATS` for counts and validation.
5. Use `BINARY` for high-throughput pipelines.
