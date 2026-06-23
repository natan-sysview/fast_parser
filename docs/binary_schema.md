# Binary Schema

`TSMP_FORMAT_BINARY` returns MessagePack bytes.

This format is intended for high-throughput program-to-program exchange across Rust, C#, Python, Java, and other runtimes.

## Version

Current binary schema:

```text
schemaVersion = 1
```

Bindings should reject unknown future schema versions unless they explicitly support them.

## Top-Level Object

The top-level value is a MessagePack map with required keys and optional diagnostic keys.

| Key | Type | Notes |
|---|---|---|
| `format` | string | Always `tsmp-binary`. |
| `schemaVersion` | unsigned integer | Currently `1`. |
| `language` | string | Public language name, for example `java`. |
| `nodes` | array | Flat list of included AST nodes. |
| `nodeCount` | unsigned integer | Same value as `TsmpResult.node_count`. |
| `hasErrors` | bool | Optional when `TSMP_FIELD_DIAGNOSTICS` is requested. |
| `errorNodeCount` | unsigned integer | Optional number of `ERROR` nodes in the full tree. |
| `missingNodeCount` | unsigned integer | Optional number of `MISSING` nodes in the full tree. |
| `errorByteCount` | unsigned integer | Optional total byte span covered by `ERROR` nodes. |

Example shape:

```text
{
  "format": "tsmp-binary",
  "schemaVersion": 1,
  "language": "java",
  "hasErrors": false,
  "errorNodeCount": 0,
  "missingNodeCount": 0,
  "errorByteCount": 0,
  "nodes": [...],
  "nodeCount": 100
}
```

## Node Object

Each node is a MessagePack map. The keys present depend on `TsmpOptions.fields`.

| Field mask | Key | Type |
|---|---|---|
| `TSMP_FIELD_ID` | `id` | unsigned integer |
| `TSMP_FIELD_PARENT_ID` | `parentId` | unsigned integer or nil |
| `TSMP_FIELD_RULE` | `rule` | string |
| `TSMP_FIELD_TEXT` | `text` | bin bytes |
| `TSMP_FIELD_RANGE` | `startLine` | unsigned integer |
| `TSMP_FIELD_RANGE` | `startColumn` | unsigned integer |
| `TSMP_FIELD_RANGE` | `endLine` | unsigned integer |
| `TSMP_FIELD_RANGE` | `endColumn` | unsigned integer |
| `TSMP_FIELD_BYTE_RANGE` | `startByte` | unsigned integer |
| `TSMP_FIELD_BYTE_RANGE` | `endByte` | unsigned integer |
| `TSMP_FIELD_CHILD_COUNT` | `childCount` | unsigned integer |
| `TSMP_FIELD_DIAGNOSTICS` | `isError` | bool |
| `TSMP_FIELD_DIAGNOSTICS` | `isMissing` | bool |
| `TSMP_FIELD_DIAGNOSTICS` | `hasError` | bool |
| `TSMP_FIELD_CHILDREN` | `children` | array |

Important:

```text
text is MessagePack bin, not MessagePack str.
```

This preserves original source bytes exactly.

## Children

`children` contains direct child summaries for each node when `TSMP_FIELD_CHILDREN` is enabled.

Each child summary can include:

| Key | Type | Notes |
|---|---|---|
| `rule` | string | Tree-sitter node type, or `token` for anonymous tokens when included. |
| `text` | bin bytes | Raw source bytes for that child. |

The child summary fields follow the same behavior as JSON:

- If `rule` is enabled, child summaries include `rule`.
- If `text` is enabled, child summaries include `text`.
- If `include_tokens` is false, anonymous tokens are skipped.

## Tree Shape

The binary schema uses a flat node list.

Parent-child relationships among included nodes are represented with:

```text
id
parentId
```

`parentId` is nil for root-level included nodes.

Consumers that want a nested tree can reconstruct it from `id` and `parentId`.

## Encoding Rules

| Value | MessagePack type |
|---|---|
| Object keys | str |
| `format` | str |
| `language` | str |
| `rule` | str |
| `text` | bin |
| IDs/counts/ranges | uint |
| Diagnostics | bool |
| Missing parent | nil |

## Compatibility Rules

For schema version 1:

- Existing keys keep their meaning.
- Optional keys may appear when requested by field flags.
- Consumers should skip unknown map keys to remain forward-compatible within the preview line.
- Breaking shape or type changes require a future schema version.
- Bindings should not rely on map key order.
- Bindings should tolerate a field being absent when the caller did not request it.

## Recommended Decoders

| Language | Decoder |
|---|---|
| Python | `msgpack` |
| C# | MessagePack-CSharp |
| Rust | `rmp` or `rmp-serde` |
| Java | msgpack-java |

## Minimal Python Decode

```python
import msgpack

document = msgpack.unpackb(result.data, raw=False)
first_node = document["nodes"][0]

assert document["format"] == "tsmp-binary"
assert document["schemaVersion"] == 1
assert isinstance(first_node["text"], bytes)
```
