#include "fastparse.h"

#include <stdio.h>
#include <string.h>

static int contains_bytes(const unsigned char *haystack, size_t haystack_len, const char *needle)
{
    size_t needle_len = strlen(needle);
    if (needle_len == 0) return 1;
    if (!haystack || haystack_len < needle_len) return 0;

    for (size_t i = 0; i <= haystack_len - needle_len; i++) {
        if (memcmp(haystack + i, needle, needle_len) == 0) return 1;
    }

    return 0;
}

static int fail_result(const char *label, const TsmpResult *result)
{
    fprintf(stderr, "%s failed: status=%d error=%s\n",
            label,
            result ? result->status : -1,
            result && result->error_message ? result->error_message : "");
    return 1;
}

int main(void)
{
    const unsigned char source[] = "class Demo { // caf\xe9\n  void m() {}\n}\n";
    TsmpResult result;

    TsmpOptions stats_options = {
        "java",
        TSMP_FORMAT_STATS,
        NULL,
        0,
        0,
        0
    };

    int status = tsmp_parse(source, sizeof(source) - 1, &stats_options, &result);
    if (status != TSMP_OK || result.status != TSMP_OK) return fail_result("stats parse", &result);
    if (result.node_count == 0 || result.data != NULL || result.length != 0) {
        tsmp_result_free(&result);
        fprintf(stderr, "stats contract failed\n");
        return 1;
    }
    tsmp_result_free(&result);

    status = fastparse_parse(source, sizeof(source) - 1, &stats_options, &result);
    if (status != TSMP_OK || result.status != TSMP_OK) return fail_result("fastparse stats parse", &result);
    if (result.node_count == 0 || result.data != NULL || result.length != 0) {
        fastparse_result_free(&result);
        fprintf(stderr, "fastparse stats contract failed\n");
        return 1;
    }
    fastparse_result_free(&result);

    TsmpOptions json_options = {
        "java",
        TSMP_FORMAT_JSON,
        "class_declaration|method_declaration",
        TSMP_FIELD_RULE | TSMP_FIELD_TEXT | TSMP_FIELD_BYTE_RANGE,
        0,
        0
    };

    status = tsmp_parse(source, sizeof(source) - 1, &json_options, &result);
    if (status != TSMP_OK || result.status != TSMP_OK) return fail_result("json parse", &result);
    if (!result.data || result.length == 0 || result.node_count == 0) {
        tsmp_result_free(&result);
        fprintf(stderr, "json contract failed\n");
        return 1;
    }
    if (!contains_bytes(result.data, result.length, "\\u00e9")) {
        tsmp_result_free(&result);
        fprintf(stderr, "json did not escape non-UTF8 byte\n");
        return 1;
    }
    tsmp_result_free(&result);

    TsmpOptions binary_options = {
        "java",
        TSMP_FORMAT_BINARY,
        "class_declaration|method_declaration",
        TSMP_FIELD_RULE | TSMP_FIELD_TEXT | TSMP_FIELD_BYTE_RANGE,
        0,
        0
    };

    status = tsmp_parse(source, sizeof(source) - 1, &binary_options, &result);
    if (status != TSMP_OK || result.status != TSMP_OK) return fail_result("binary parse", &result);
    if (!result.data || result.length == 0 || result.node_count == 0) {
        tsmp_result_free(&result);
        fprintf(stderr, "binary contract failed\n");
        return 1;
    }
    if (!contains_bytes(result.data, result.length, "tsmp-binary")) {
        tsmp_result_free(&result);
        fprintf(stderr, "binary output did not include format marker\n");
        return 1;
    }
    tsmp_result_free(&result);

    status = tsmp_parse((const unsigned char *)"", 0, &stats_options, &result);
    if (status != TSMP_OK || result.status != TSMP_OK) return fail_result("empty parse", &result);
    if (result.node_count == 0) {
        tsmp_result_free(&result);
        fprintf(stderr, "empty source should still produce a root node\n");
        return 1;
    }
    tsmp_result_free(&result);

    return 0;
}
