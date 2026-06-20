# FastParse Contracts

This document defines the public behavior expected by applications and bindings.

## Core Boundary

FastParse is memory-only.

The parent application owns:

- Reading files.
- Walking directories.
- Choosing threads.
- Creating databases.
- Persisting results.
- Logging and progress reporting.
- Mapping AST rows into domain objects.

FastParse owns:

- Parsing one source buffer.
- Traversing the Tree-sitter AST.
- Filtering nodes by rule name.
- Filtering fields by bit mask.
- Serializing the requested output into memory.

## Input Contract

Native input:

```text
source: const unsigned char *
source_len: size_t
language: string
```

Rules:

- `source` points to immutable bytes.
- The source buffer must stay valid until `fastparse_parse` returns.
- FastParse does not assume the source is UTF-8.
- Byte offsets are based on the exact input bytes.
- Text fields are slices of the original source bytes serialized according to the chosen output format.

Current language names:

```text
java
```

## Output Contract

Every parse returns a `TsmpResult`.

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

- `data` is owned by FastParse until `fastparse_result_free`.
- `error_message` is owned by FastParse until `fastparse_result_free`.
- Bindings should copy `data` into runtime-owned memory before freeing the result.
- `node_count` is populated for every successful format.
- `TSMP_FORMAT_STATS` returns `data = NULL` and `length = 0`.

## Rule Filter Contract

`include_rules` is a pipe-separated exact-match list:

```text
class_declaration|method_declaration|field_declaration
```

Behavior:

- `NULL` means all named AST nodes.
- Empty string means all named AST nodes.
- Matching is exact and case-sensitive.
- Anonymous tokens are not included as top-level nodes.

## Field Filter Contract

`fields = 0` means all fields.

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
TSMP_FIELD_ALL
```

Production callers should request only fields they need.

## Threading Contract

`fastparse_parse` is thread-safe per call.

Safe:

- Many threads parsing different immutable source buffers.
- Many threads parsing the same immutable source buffer.
- One result object per active call.

Not safe:

- Mutating a source buffer while parsing it.
- Sharing one mutable `TsmpResult` across active calls.
- Freeing one result more than once.

FastParse does not create worker threads.

## Stability Contract

Publicly documented behavior should be treated as stable within a release line:

- C struct layout.
- Native function names.
- Format constants.
- Field constants.
- Binary `schemaVersion`.
- Error codes.

Compatibility aliases:

```text
tsmp_version
tsmp_parse
tsmp_result_free
```

These exist for older internal users. New integrations should call:

```text
fastparse_version
fastparse_parse
fastparse_result_free
```
