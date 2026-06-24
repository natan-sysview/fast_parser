# Output Formats

FastParse uses one filtering contract across all formats:

```text
language
include_rules
fields
include_tokens
```

Only serialization changes.

## JSON

Native constant:

```text
TSMP_FORMAT_JSON
```

Use JSON for:

- Debugging.
- Documentation.
- Initial integration.
- Development-time rule discovery.

Top-level shape:

```json
{
  "language": "java",
  "hasErrors": false,
  "errorNodeCount": 0,
  "missingNodeCount": 0,
  "errorByteCount": 0,
  "nodes": [],
  "nodeCount": 0
}
```

Node fields depend on the requested field mask.

Diagnostic top-level fields appear when `TSMP_FIELD_DIAGNOSTICS` is requested, or when the default/all field set is used. Per-node diagnostics are `isError`, `isMissing`, and `hasError`.

## CSV

Native constant:

```text
TSMP_FORMAT_CSV
```

Use CSV for:

- Spreadsheet inspection.
- Quick tabular exports.
- Loading selected rules into data tools.

CSV columns depend on the requested field mask.

When diagnostics are requested, CSV adds flat columns:

```text
is_error,is_missing,has_error
```

## Binary MessagePack

Native constant:

```text
TSMP_FORMAT_BINARY
```

Use binary for:

- High-performance bindings.
- Large-scale program-to-program exchange.
- Avoiding JSON escaping overhead.
- Preserving source text as raw bytes.

Top-level shape:

```text
format: "tsmp-binary"
schemaVersion: 1
language: string
nodes: array
nodeCount: integer
hasErrors: bool               optional diagnostics
errorNodeCount: integer       optional diagnostics
missingNodeCount: integer     optional diagnostics
errorByteCount: integer       optional diagnostics
```

Important:

```text
node.text is MessagePack bin bytes
```

See [Binary MessagePack Schema](binary_schema.md).

## Stats

Native constant:

```text
TSMP_FORMAT_STATS
```

Use stats for:

- Measuring parse/traverse speed.
- Counting matching rules.
- Avoiding serialization cost.

Result behavior:

```text
result.data = NULL
result.length = 0
result.node_count = matching node count
```

## Diagnostics

Native constant:

```text
TSMP_FORMAT_DIAGNOSTICS
```

Use diagnostics for:

- Large grammar quality scans.
- Comparing language extensions.
- Finding files that Tree-sitter recovered with `ERROR` or `MISSING` nodes.
- Storing parse-quality metrics without storing AST payloads.

Result behavior:

```text
result.data = small UTF-8 JSON object
result.length > 0
result.node_count = full named node count
```

Shape:

```json
{
  "language": "cobol",
  "nodeCount": 29584,
  "hasErrors": true,
  "errorNodeCount": 3,
  "missingNodeCount": 1,
  "errorByteCount": 1204
}
```

This format does not include a `nodes` array and ignores field selection. Tree-sitter exposes error flags on nodes; FastParse walks the tree once in C to aggregate the counters.

## Recommended Usage

Exploration:

```text
format = json
rules = all
fields = all
```

Production:

```text
format = binary
rules = exact list of needed grammar rules
fields = only fields needed by the parent application
```

Counting:

```text
format = stats
rules = exact list to count
fields = ignored for output
```

Grammar quality scan:

```text
format = diagnostics
rules = ignored for output
fields = ignored for output
```
