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
    return "fastparse-c-api/0.4.0";
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
        options->format != TSMP_FORMAT_BINARY &&
        options->format != TSMP_FORMAT_DIAGNOSTICS) {
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
