#include "../include/tsmp.h"

#include "tsmp_languages.h"
#include "tsmp_render.h"

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <tree_sitter/api.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif

const char *tsmp_version(void)
{
    return "fastparse-c-api/0.5.0";
}

typedef struct {
    const unsigned char *data;
    size_t length;
    unsigned char *owned;
} NormalizedSource;

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

static void language_load_result_init(FastParseLanguageLoadResult *result)
{
    if (!result) return;
    result->status = TSMP_OK;
    result->language = NULL;
    result->display_name = NULL;
    result->error_message = NULL;
}

static int language_load_result_set_error(
    FastParseLanguageLoadResult *result,
    int status,
    const char *message)
{
    if (!result) return status;

    result->status = status;
    result->language = NULL;
    result->display_name = NULL;
    result->error_message = copy_text(message);
    if (!result->error_message && message) {
        result->status = TSMP_ERROR_OUT_OF_MEMORY;
    }

    return result->status;
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

static int is_ascii_space(unsigned char value)
{
    return value == ' ' || value == '\t' || value == '\r' || value == '\n';
}

static size_t trim_trailing_ascii_space(const unsigned char *source, size_t start, size_t end)
{
    while (end > start && is_ascii_space(source[end - 1])) {
        end--;
    }
    return end;
}

static int equals_marker(const unsigned char *source, size_t start, size_t end, const char *marker)
{
    size_t marker_len = strlen(marker);
    return end >= start && end - start == marker_len && memcmp(source + start, marker, marker_len) == 0;
}

static int is_cobol_legacy_trailer_line(const unsigned char *source, size_t start, size_t end)
{
    while (start < end && (source[start] == ' ' || source[start] == '\t' || source[start] == '\r')) {
        start++;
    }
    while (end > start && (source[end - 1] == ' ' || source[end - 1] == '\t' || source[end - 1] == '\r')) {
        end--;
    }

    return equals_marker(source, start, end, "FHA") || equals_marker(source, start, end, "*");
}

static int language_is(const char *language, const char *expected)
{
    return language && strcmp(language, expected) == 0;
}

static int normalize_cobol_fixed_legacy(
    const unsigned char *source,
    size_t source_len,
    NormalizedSource *out_source)
{
    size_t start = 0;
    size_t end = source_len;
    int changed = 0;

    if (source_len >= 3 &&
        source[0] == 0xEF &&
        source[1] == 0xBB &&
        source[2] == 0xBF) {
        start = 3;
        changed = 1;
    }

    while (end > start) {
        size_t candidate_end = trim_trailing_ascii_space(source, start, end);
        if (candidate_end > start &&
            (source[candidate_end - 1] == 0x1A ||
             source[candidate_end - 1] == 0x7F ||
             source[candidate_end - 1] == 0x00)) {
            end = candidate_end - 1;
            changed = 1;
            continue;
        }

        size_t line_start = candidate_end;
        while (line_start > start && source[line_start - 1] != '\n') {
            line_start--;
        }
        if (line_start < candidate_end &&
            is_cobol_legacy_trailer_line(source, line_start, candidate_end)) {
            end = line_start;
            changed = 1;
            continue;
        }

        break;
    }

    if (!changed) {
        return TSMP_OK;
    }

    size_t normalized_len = end - start;
    unsigned char *copy = NULL;
    if (normalized_len > 0) {
        copy = malloc(normalized_len);
        if (!copy) return TSMP_ERROR_OUT_OF_MEMORY;
        memcpy(copy, source + start, normalized_len);
    }

    out_source->data = copy ? copy : (const unsigned char *)"";
    out_source->length = normalized_len;
    out_source->owned = copy;
    return TSMP_OK;
}

static int normalize_source(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptionsV2 *options,
    NormalizedSource *out_source)
{
    out_source->data = source_len == 0 ? (const unsigned char *)"" : source;
    out_source->length = source_len;
    out_source->owned = NULL;

    if (options->normalization == TSMP_NORMALIZATION_NONE || source_len == 0) {
        return TSMP_OK;
    }

    if (options->normalization == TSMP_NORMALIZATION_COBOL_FIXED_LEGACY ||
        (options->normalization == TSMP_NORMALIZATION_AUTO_SAFE && language_is(options->language, "cobol"))) {
        return normalize_cobol_fixed_legacy(source, source_len, out_source);
    }

    return TSMP_OK;
}

static void normalized_source_free(NormalizedSource *source)
{
    if (!source) return;
    free(source->owned);
    source->data = NULL;
    source->length = 0;
    source->owned = NULL;
}

static int tsmp_parse_internal(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptionsV2 *options,
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

    if (options->format != TSMP_FORMAT_JSON &&
        options->format != TSMP_FORMAT_CSV &&
        options->format != TSMP_FORMAT_STATS &&
        options->format != TSMP_FORMAT_BINARY &&
        options->format != TSMP_FORMAT_DIAGNOSTICS) {
        return result_set_error(out_result, TSMP_ERROR_UNSUPPORTED_FORMAT, "Unsupported output format.");
    }

    if (options->normalization != TSMP_NORMALIZATION_AUTO_SAFE &&
        options->normalization != TSMP_NORMALIZATION_NONE &&
        options->normalization != TSMP_NORMALIZATION_COBOL_FIXED_LEGACY) {
        return result_set_error(out_result, TSMP_ERROR_INVALID_ARGUMENT, "Unsupported normalization mode.");
    }

    const TSLanguage *language = tsmp_find_language(options->language);
    if (!language) {
        return result_set_error(out_result, TSMP_ERROR_UNSUPPORTED_LANGUAGE, "Unsupported language.");
    }

    NormalizedSource normalized_source;
    int normalize_status = normalize_source(source, source_len, options, &normalized_source);
    if (normalize_status != TSMP_OK) {
        return result_set_error(out_result, normalize_status, "Failed to normalize source.");
    }

    if (normalized_source.length > UINT32_MAX) {
        normalized_source_free(&normalized_source);
        return result_set_error(
            out_result,
            TSMP_ERROR_INVALID_ARGUMENT,
            "source_len exceeds the current Tree-sitter input limit.");
    }

    TSParser *parser = ts_parser_new();
    if (!parser) {
        normalized_source_free(&normalized_source);
        return result_set_error(out_result, TSMP_ERROR_OUT_OF_MEMORY, "Could not allocate Tree-sitter parser.");
    }

    if (!ts_parser_set_language(parser, language)) {
        ts_parser_delete(parser);
        normalized_source_free(&normalized_source);
        return result_set_error(
            out_result,
            TSMP_ERROR_PARSE_FAILED,
            "Grammar is incompatible with the Tree-sitter runtime.");
    }

    const char *parse_source = normalized_source.length == 0 ? "" : (const char *)normalized_source.data;
    TSTree *tree = ts_parser_parse_string(
        parser,
        NULL,
        parse_source,
        (uint32_t)normalized_source.length);
    if (!tree) {
        ts_parser_delete(parser);
        normalized_source_free(&normalized_source);
        return result_set_error(out_result, TSMP_ERROR_PARSE_FAILED, "Tree-sitter parse failed.");
    }

    TsmpOptions render_options = {
        options->language,
        options->format,
        options->include_rules,
        options->fields,
        options->include_tokens,
        options->pretty
    };
    int status = tsmp_render_tree(normalized_source.data, normalized_source.length, &render_options, tree, out_result);
    if (status != TSMP_OK && !out_result->error_message) {
        result_set_error(out_result, status, "Failed to render AST.");
    }

    ts_tree_delete(tree);
    ts_parser_delete(parser);
    normalized_source_free(&normalized_source);
    return out_result->status;
}

int tsmp_parse(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptions *options,
    TsmpResult *out_result)
{
    if (!options) {
        return tsmp_parse_internal(source, source_len, NULL, out_result);
    }

    TsmpOptionsV2 options_v2 = {
        options->language,
        options->format,
        options->include_rules,
        options->fields,
        options->include_tokens,
        options->pretty,
        TSMP_NORMALIZATION_NONE
    };
    return tsmp_parse_internal(source, source_len, &options_v2, out_result);
}

int tsmp_parse_v2(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptionsV2 *options,
    TsmpResult *out_result)
{
    return tsmp_parse_internal(source, source_len, options, out_result);
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

int fastparse_parse_v2(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptionsV2 *options,
    TsmpResult *out_result)
{
    return tsmp_parse_v2(source, source_len, options, out_result);
}

void fastparse_result_free(TsmpResult *result)
{
    tsmp_result_free(result);
}

typedef const FastParseLanguageDescriptor *(*FastParseLanguageDescriptorFn)(void);

int fastparse_load_language_extension(
    const char *path,
    FastParseLanguageLoadResult *out_result)
{
    if (!out_result) return TSMP_ERROR_INVALID_ARGUMENT;
    language_load_result_init(out_result);

    if (!path || !*path) {
        return language_load_result_set_error(
            out_result,
            TSMP_ERROR_INVALID_ARGUMENT,
            "Language extension path is required.");
    }

#ifdef _WIN32
    HMODULE handle = LoadLibraryA(path);
    if (!handle) {
        return language_load_result_set_error(
            out_result,
            TSMP_ERROR_EXTENSION_LOAD,
            "Could not load language extension library.");
    }
    FastParseLanguageDescriptorFn descriptor_fn =
        (FastParseLanguageDescriptorFn)(void *)GetProcAddress(handle, "fastparse_language_extension_descriptor");
    if (!descriptor_fn) {
        FreeLibrary(handle);
        return language_load_result_set_error(
            out_result,
            TSMP_ERROR_EXTENSION_LOAD,
            "Language extension descriptor symbol was not found.");
    }
#else
    void *handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (!handle) {
        const char *detail = dlerror();
        return language_load_result_set_error(
            out_result,
            TSMP_ERROR_EXTENSION_LOAD,
            detail ? detail : "Could not load language extension library.");
    }
    dlerror();
    FastParseLanguageDescriptorFn descriptor_fn =
        (FastParseLanguageDescriptorFn)dlsym(handle, "fastparse_language_extension_descriptor");
    const char *symbol_error = dlerror();
    if (symbol_error || !descriptor_fn) {
        dlclose(handle);
        return language_load_result_set_error(
            out_result,
            TSMP_ERROR_EXTENSION_LOAD,
            symbol_error ? symbol_error : "Language extension descriptor symbol was not found.");
    }
#endif

    int status = tsmp_register_language_extension(descriptor_fn(), handle, out_result);
    if (status != TSMP_OK) {
#ifdef _WIN32
        FreeLibrary(handle);
#else
        dlclose(handle);
#endif
    }
    return status;
}

int fastparse_language_available(const char *language)
{
    return tsmp_language_available(language);
}

void fastparse_language_load_result_free(FastParseLanguageLoadResult *result)
{
    if (!result) return;
    free(result->language);
    free(result->display_name);
    free(result->error_message);
    language_load_result_init(result);
}
