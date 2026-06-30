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

    TsmpOptions diagnostics_options = {
        "java",
        TSMP_FORMAT_DIAGNOSTICS,
        NULL,
        0,
        0,
        0
    };

    const unsigned char broken_source[] = "class Demo { void broken( { }";
    status = tsmp_parse(broken_source, sizeof(broken_source) - 1, &diagnostics_options, &result);
    if (status != TSMP_OK || result.status != TSMP_OK) return fail_result("diagnostics parse", &result);
    if (!result.data || result.length == 0 || result.node_count == 0) {
        tsmp_result_free(&result);
        fprintf(stderr, "diagnostics contract failed\n");
        return 1;
    }
    if (!contains_bytes(result.data, result.length, "\"hasErrors\":true") ||
        contains_bytes(result.data, result.length, "\"nodes\"")) {
        tsmp_result_free(&result);
        fprintf(stderr, "diagnostics payload did not match expected shape\n");
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

    TsmpOptionsV2 v2_options = {
        "java",
        TSMP_FORMAT_STATS,
        NULL,
        0,
        0,
        0,
        TSMP_NORMALIZATION_AUTO_SAFE
    };

    status = fastparse_parse_v2(source, sizeof(source) - 1, &v2_options, &result);
    if (status != TSMP_OK || result.status != TSMP_OK) return fail_result("fastparse v2 stats parse", &result);
    if (result.node_count == 0 || result.data != NULL || result.length != 0) {
        fastparse_result_free(&result);
        fprintf(stderr, "fastparse v2 stats contract failed\n");
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

    const unsigned char query[] =
        "(method_declaration name: (identifier) @method.name) @method";
    TsmpQueryOptions query_options = {
        "java",
        TSMP_FORMAT_JSON,
        0,
        0,
        0,
        1,
        0,
        TSMP_NORMALIZATION_AUTO_SAFE
    };
    status = fastparse_query(source, sizeof(source) - 1, query, sizeof(query) - 1, &query_options, &result);
    if (status != TSMP_OK || result.status != TSMP_OK) return fail_result("fastparse query json", &result);
    if (!result.data || result.length == 0 || result.node_count != 2) {
        fastparse_result_free(&result);
        fprintf(stderr, "query json contract failed\n");
        return 1;
    }
    if (!contains_bytes(result.data, result.length, "\"name\":\"method.name\"") ||
        !contains_bytes(result.data, result.length, "\"rule\":\"method_declaration\"") ||
        !contains_bytes(result.data, result.length, "\"matchCount\":1") ||
        !contains_bytes(result.data, result.length, "\"captureCount\":2")) {
        fastparse_result_free(&result);
        fprintf(stderr, "query json payload did not match expected shape\n");
        return 1;
    }
    fastparse_result_free(&result);

    query_options.format = TSMP_FORMAT_STATS;
    status = tsmp_query(source, sizeof(source) - 1, query, sizeof(query) - 1, &query_options, &result);
    if (status != TSMP_OK || result.status != TSMP_OK) return fail_result("query stats", &result);
    if (result.node_count != 2 || result.length != 1 || result.data != NULL) {
        tsmp_result_free(&result);
        fprintf(stderr, "query stats contract failed\n");
        return 1;
    }
    tsmp_result_free(&result);

    const unsigned char bad_query[] = "(missing_node) @bad";
    query_options.format = TSMP_FORMAT_JSON;
    status = tsmp_query(source, sizeof(source) - 1, bad_query, sizeof(bad_query) - 1, &query_options, &result);
    if (status != TSMP_ERROR_QUERY_COMPILE || result.status != TSMP_ERROR_QUERY_COMPILE) {
        tsmp_result_free(&result);
        fprintf(stderr, "invalid query should fail during query compilation\n");
        return 1;
    }
    tsmp_result_free(&result);

    return 0;
}
