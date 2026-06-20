# Encoding And Bytes Contract

TSMP treats source input as bytes owned by the caller.

The core parsing API is:

```c
int tsmp_parse(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptions *options,
    TsmpResult *out_result);
```

## Input Contract

`source` is an opaque byte buffer.

TSMP does not:

- Open files.
- Detect encoding.
- Convert encodings.
- Normalize line endings.
- Remove byte-order marks.
- Validate that the input is UTF-8.

The parent application decides how to read bytes from disk, network, database, editor memory, or any other source.

## Empty Input

Empty source is valid:

```c
source_len = 0;
```

For an empty Java source, Tree-sitter still returns a root `program` node.

## Size Limit

The public API uses `size_t`, but the current Tree-sitter parse call accepts a 32-bit length.

Current contract:

```text
source_len <= UINT32_MAX
```

If the input exceeds that limit, `tsmp_parse` returns `TSMP_ERROR_INVALID_ARGUMENT`.

This avoids silent truncation.

## Tree-Sitter Interpretation

Tree-sitter grammars operate over the byte stream. Rule names, byte ranges, and syntax structure are produced by Tree-sitter.

This means TSMP can parse files that contain non-ASCII bytes, but it does not promise that every grammar will interpret every legacy encoding semantically the same way a compiler or IDE would.

For exact extraction, prefer byte ranges:

```text
startByte
endByte
```

The caller can slice the original source buffer using those byte offsets.

## Line And Column Contract

`startLine` and `endLine` are 1-based.

`startColumn` and `endColumn` are Tree-sitter byte columns, not visual columns and not Unicode code-point indexes.

This matters for tabs, multi-byte UTF-8, Latin-1 bytes, Windows-1252 bytes, and mixed encodings.

If a binding needs editor-style columns, it should compute them in the parent language using the same decoding policy that the editor uses.

## JSON Output

JSON output is always valid UTF-8 JSON.

When source text contains bytes outside printable ASCII, TSMP escapes them in JSON strings:

```text
\u00e1
\u00f1
\u0080
```

This keeps JSON parsers happy even when the original file was not UTF-8.

Important consequence:

- `text` in JSON is safe structured text.
- `text` is not a byte-for-byte transport for arbitrary source bytes.
- Use `startByte` and `endByte` when exact byte recovery matters.

## CSV Output

CSV output is a byte-oriented text format.

TSMP quotes fields, doubles quotes inside fields, and writes non-null source bytes as they appeared. Null bytes are represented as:

```text
\0
```

CSV consumers may still apply their own decoding assumptions. For source files with unknown or mixed encodings, JSON plus byte ranges is safer.

## Binary Output

Binary output uses MessagePack.

Unlike JSON, the `text` field is encoded as MessagePack `bin`, so it preserves the original source bytes exactly.

Recommended decoding policy:

```text
rule/language/keys -> strings
text               -> bytes
byte ranges        -> integers
```

This is the safest format when callers need both high throughput and byte-exact source slices.

## Recommended Binding Policy

Bindings should expose two levels:

1. Raw bytes API.
2. Convenience string API.

Recommended shape:

```text
parse_bytes(bytes, options)
parse_text(text, encoding="utf-8", options)
```

The convenience string API should encode text before passing it to TSMP. The raw bytes API should not modify the buffer.

## Recommended Production Fields

For maximum encoding safety:

```text
rule,byte_range
```

For human inspection:

```text
rule,text,range
```

For exact extraction plus debugging:

```text
rule,text,range,byte_range
```
