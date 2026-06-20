#include <stdio.h>
#include <string.h>

#include "fastparse.h"

static int contains_bytes(const unsigned char *data, size_t data_len, const char *needle)
{
    size_t needle_len = strlen(needle);
    size_t index;

    if (needle_len == 0 || data_len < needle_len) {
        return 0;
    }

    for (index = 0; index <= data_len - needle_len; index++) {
        if (memcmp(data + index, needle, needle_len) == 0) {
            return 1;
        }
    }
    return 0;
}

int main(void)
{
    const unsigned char source[] =
        "class Demo { void run() { System.out.println(\"fastparse\"); } }";
    const char *rules = "method_declaration";
    TsmpOptions options;
    TsmpResult result;

    memset(&options, 0, sizeof(options));
    memset(&result, 0, sizeof(result));

    options.language = "java";
    options.format = TSMP_FORMAT_JSON;
    options.include_rules = rules;
    options.fields = TSMP_FIELD_RULE | TSMP_FIELD_TEXT | TSMP_FIELD_BYTE_RANGE;

    if (fastparse_parse(source, sizeof(source) - 1, &options, &result) != TSMP_OK) {
        fprintf(stderr, "fastparse_parse failed: %s\n",
                result.error_message ? result.error_message : "unknown error");
        fastparse_result_free(&result);
        return 1;
    }

    if (result.node_count != 1 || result.data == NULL ||
        !contains_bytes(result.data, result.length, "method_declaration")) {
        fprintf(stderr, "unexpected parse result: nodes=%zu length=%zu\n",
                result.node_count, result.length);
        fastparse_result_free(&result);
        return 1;
    }

    printf("FastParse C smoke test OK\n");
    printf("Library : %s\n", fastparse_version());
    printf("Nodes   : %zu\n", result.node_count);

    fastparse_result_free(&result);
    return 0;
}
