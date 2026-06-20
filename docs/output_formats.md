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
  "nodes": [],
  "nodeCount": 0
}
```

Node fields depend on the requested field mask.

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
