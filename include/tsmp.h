#ifndef TSMP_H
#define TSMP_H

#include <stddef.h>

#ifdef _WIN32
  #ifdef TSMP_BUILD_SHARED
    #define TSMP_API __declspec(dllexport)
  #else
    #define TSMP_API __declspec(dllimport)
  #endif
#else
  #define TSMP_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

#define TSMP_OK 0
#define TSMP_ERROR_INVALID_ARGUMENT 1
#define TSMP_ERROR_UNSUPPORTED_LANGUAGE 2
#define TSMP_ERROR_PARSE_FAILED 3
#define TSMP_ERROR_IO 4
#define TSMP_ERROR_UNSUPPORTED_FORMAT 5
#define TSMP_ERROR_OUT_OF_MEMORY 6

typedef enum {
    TSMP_FORMAT_JSON = 1,
    TSMP_FORMAT_CSV = 2,
    TSMP_FORMAT_STATS = 3,
    TSMP_FORMAT_BINARY = 4
} TsmpFormat;

typedef enum {
    TSMP_FIELD_ID          = 1u << 0,
    TSMP_FIELD_PARENT_ID   = 1u << 1,
    TSMP_FIELD_RULE        = 1u << 2,
    TSMP_FIELD_TEXT        = 1u << 3,
    TSMP_FIELD_RANGE       = 1u << 4,
    TSMP_FIELD_BYTE_RANGE  = 1u << 5,
    TSMP_FIELD_CHILD_COUNT = 1u << 6,
    TSMP_FIELD_CHILDREN    = 1u << 7,
    TSMP_FIELD_DIAGNOSTICS = 1u << 8,
    TSMP_FIELD_ALL         = 0xFFFFFFFFu
} TsmpFieldMask;

typedef struct {
    const char *language;
    TsmpFormat format;
    const char *include_rules; /* Pipe-separated exact rule names. NULL/empty = all. */
    unsigned int fields;       /* 0 = TSMP_FIELD_ALL. */
    int include_tokens;        /* 0 = named nodes only. Non-zero includes direct token children. */
    int pretty;                /* Reserved for formatted JSON. */
} TsmpOptions;

typedef struct {
    int status;
    unsigned char *data;
    size_t length;
    size_t node_count;
    char *error_message;
} TsmpResult;

TSMP_API const char *tsmp_version(void);

TSMP_API int tsmp_parse(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptions *options,
    TsmpResult *out_result);

TSMP_API void tsmp_result_free(TsmpResult *result);

/* FastParse branded aliases. The tsmp_* ABI remains supported for compatibility. */
TSMP_API const char *fastparse_version(void);

TSMP_API int fastparse_parse(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptions *options,
    TsmpResult *out_result);

TSMP_API void fastparse_result_free(TsmpResult *result);

#ifdef __cplusplus
}
#endif

#endif /* TSMP_H */
