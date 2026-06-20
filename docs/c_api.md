# C API

The C API is the source of truth for every binding.

## Header

```c
#include "fastparse.h"
```

`fastparse.h` includes the underlying declarations from `tsmp.h`. The `tsmp_*` names remain available as compatibility aliases, but new code should use `fastparse_*`.

## Functions

```c
const char *fastparse_version(void);
```

Returns a static UTF-8 string such as:

```text
fastparse-c-api/0.3.0
```

```c
int fastparse_parse(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptions *options,
    TsmpResult *out_result);
```

Parses one source buffer and fills `out_result`.

```c
void fastparse_result_free(TsmpResult *result);
```

Releases `result->data` and `result->error_message`, then clears result fields.

## Options

```c
typedef struct {
    const char *language;
    TsmpFormat format;
    const char *include_rules;
    unsigned int fields;
    int include_tokens;
    int pretty;
} TsmpOptions;
```

Defaults:

```c
TsmpOptions options = {
    .language = "java",
    .format = TSMP_FORMAT_JSON,
    .include_rules = NULL,
    .fields = 0,
    .include_tokens = 0,
    .pretty = 0
};
```

Meaning:

- `include_rules = NULL` or empty means all named nodes.
- `fields = 0` means all fields.
- `include_tokens = 0` keeps anonymous tokens out of top-level output.
- `pretty` is reserved for future formatted JSON.

## Example: JSON Methods

```c
#include "fastparse.h"

int parse_methods(const unsigned char *source, size_t source_len)
{
    TsmpOptions options = {
        .language = "java",
        .format = TSMP_FORMAT_JSON,
        .include_rules = "method_declaration",
        .fields = TSMP_FIELD_RULE | TSMP_FIELD_TEXT | TSMP_FIELD_BYTE_RANGE,
        .include_tokens = 0,
        .pretty = 0
    };

    TsmpResult result = {0};
    int status = fastparse_parse(source, source_len, &options, &result);

    if (status != TSMP_OK || result.status != TSMP_OK) {
        const char *message = result.error_message ? result.error_message : "unknown error";
        /* log or propagate message */
        fastparse_result_free(&result);
        return status != TSMP_OK ? status : result.status;
    }

    /* result.data contains result.length JSON bytes */

    fastparse_result_free(&result);
    return TSMP_OK;
}
```

## Example: Binary For Bindings

```c
TsmpOptions options = {
    .language = "java",
    .format = TSMP_FORMAT_BINARY,
    .include_rules = "class_declaration|method_declaration",
    .fields = TSMP_FIELD_ID |
              TSMP_FIELD_PARENT_ID |
              TSMP_FIELD_RULE |
              TSMP_FIELD_TEXT |
              TSMP_FIELD_BYTE_RANGE,
    .include_tokens = 0,
    .pretty = 0
};
```

The result data is MessagePack bytes. Bindings should copy the buffer before freeing the native result.

## Status Codes

```text
TSMP_OK                        0
TSMP_ERROR_INVALID_ARGUMENT    1
TSMP_ERROR_UNSUPPORTED_LANGUAGE 2
TSMP_ERROR_PARSE_FAILED        3
TSMP_ERROR_IO                  4
TSMP_ERROR_UNSUPPORTED_FORMAT  5
TSMP_ERROR_OUT_OF_MEMORY       6
```

`TSMP_ERROR_IO` is reserved for compatibility. The FastParse core does not perform file I/O.

## Memory Ownership

Call `fastparse_result_free` exactly once for every initialized result passed to `fastparse_parse`.

Bindings should use this pattern:

```text
call native parse
copy result.data if needed
copy result.error_message if needed
free native result in finally/defer/drop
return runtime-owned data
```
