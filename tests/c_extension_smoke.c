#include "../include/tsmp.h"

#include <stdio.h>
#include <string.h>

static int expect(int condition, const char *message)
{
    if (!condition) {
        fprintf(stderr, "%s\n", message);
        return 1;
    }
    return 0;
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "usage: %s /path/to/language-extension\n", argv[0]);
        return 1;
    }

    if (expect(!fastparse_language_available("java_extension"), "java_extension should not be available before load")) {
        return 1;
    }

    FastParseLanguageLoadResult load_result;
    int status = fastparse_load_language_extension(argv[1], &load_result);
    if (status != TSMP_OK || load_result.status != TSMP_OK) {
        fprintf(stderr, "extension load failed: %s\n", load_result.error_message ? load_result.error_message : "no detail");
        fastparse_language_load_result_free(&load_result);
        return 1;
    }

    if (expect(load_result.language && strcmp(load_result.language, "java_extension") == 0, "loaded language mismatch")) {
        fastparse_language_load_result_free(&load_result);
        return 1;
    }
    fastparse_language_load_result_free(&load_result);

    if (expect(fastparse_language_available("java_extension"), "java_extension should be available after load")) {
        return 1;
    }

    const unsigned char source[] = "class Demo { void run() {} }";
    TsmpOptions options = {
        "java_extension",
        TSMP_FORMAT_JSON,
        "method_declaration",
        TSMP_FIELD_RULE | TSMP_FIELD_TEXT,
        0,
        0
    };
    TsmpResult result;
    status = fastparse_parse(source, sizeof(source) - 1, &options, &result);
    if (status != TSMP_OK || result.status != TSMP_OK) {
        fprintf(stderr, "parse failed: %s\n", result.error_message ? result.error_message : "no detail");
        fastparse_result_free(&result);
        return 1;
    }

    int ok = result.node_count == 1 && result.data && strstr((const char *)result.data, "method_declaration");
    fastparse_result_free(&result);
    return expect(ok, "extension parse did not return the expected method_declaration");
}
