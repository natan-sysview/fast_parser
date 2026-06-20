#include "../include/tsmp.h"

#include "tsmp_languages.h"
#include "tsmp_render.h"

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <tree_sitter/api.h>

const char *tsmp_version(void)
{
    return "fastparse-c-api/0.3.0";
}

static char *copy_text(const char *value)
{
    const char *safe = value ? value : "";
    size_t len = strlen(safe);
    char *copy = malloc(len + 1);
    if (!copy) return NULL;
    memcpy(copy, safe, len + 1);
    return copy;
}

static void result_init(TsmpResult *result)
{
    if (!result) return;
    result->status = TSMP_OK;
    result->data = NULL;
    result->length = 0;
    result->node_count = 0;
    result->error_message = NULL;
}

static int result_set_error(TsmpResult *result, int status, const char *message)
{
    if (!result) return status;

    result->status = status;
    result->data = NULL;
    result->length = 0;
    result->node_count = 0;
    result->error_message = copy_text(message);
    if (!result->error_message && message) {
        result->status = TSMP_ERROR_OUT_OF_MEMORY;
    }

    return result->status;
}

int tsmp_parse(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptions *options,
    TsmpResult *out_result)
{
    if (!out_result) return TSMP_ERROR_INVALID_ARGUMENT;
    result_init(out_result);

    if ((source_len > 0 && !source) || !options || !options->language) {
        return result_set_error(
            out_result,
            TSMP_ERROR_INVALID_ARGUMENT,
            "source, options, and options.language are required.");
    }

    if (source_len > UINT32_MAX) {
        return result_set_error(
            out_result,
            TSMP_ERROR_INVALID_ARGUMENT,
            "source_len exceeds the current Tree-sitter input limit.");
    }

    if (options->format != TSMP_FORMAT_JSON &&
        options->format != TSMP_FORMAT_CSV &&
        options->format != TSMP_FORMAT_STATS &&
        options->format != TSMP_FORMAT_BINARY) {
        return result_set_error(out_result, TSMP_ERROR_UNSUPPORTED_FORMAT, "Unsupported output format.");
    }

    const TSLanguage *language = tsmp_find_language(options->language);
    if (!language) {
        return result_set_error(out_result, TSMP_ERROR_UNSUPPORTED_LANGUAGE, "Unsupported language.");
    }

    TSParser *parser = ts_parser_new();
    if (!parser) {
        return result_set_error(out_result, TSMP_ERROR_OUT_OF_MEMORY, "Could not allocate Tree-sitter parser.");
    }

    if (!ts_parser_set_language(parser, language)) {
        ts_parser_delete(parser);
        return result_set_error(
            out_result,
            TSMP_ERROR_PARSE_FAILED,
            "Grammar is incompatible with the Tree-sitter runtime.");
    }

    const char *parse_source = source_len == 0 ? "" : (const char *)source;
    TSTree *tree = ts_parser_parse_string(
        parser,
        NULL,
        parse_source,
        (uint32_t)source_len);
    if (!tree) {
        ts_parser_delete(parser);
        return result_set_error(out_result, TSMP_ERROR_PARSE_FAILED, "Tree-sitter parse failed.");
    }

    int status = tsmp_render_tree(source, source_len, options, tree, out_result);
    if (status != TSMP_OK && !out_result->error_message) {
        result_set_error(out_result, status, "Failed to render AST.");
    }

    ts_tree_delete(tree);
    ts_parser_delete(parser);
    return out_result->status;
}

void tsmp_result_free(TsmpResult *result)
{
    if (!result) return;
    free(result->data);
    free(result->error_message);
    result_init(result);
}

const char *fastparse_version(void)
{
    return tsmp_version();
}

int fastparse_parse(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptions *options,
    TsmpResult *out_result)
{
    return tsmp_parse(source, source_len, options, out_result);
}

void fastparse_result_free(TsmpResult *result)
{
    tsmp_result_free(result);
}
