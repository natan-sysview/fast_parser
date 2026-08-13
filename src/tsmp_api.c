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

static const uint16_t CP037_TO_UNICODE[256] = {
    0x0000, 0x0001, 0x0002, 0x0003, 0x009C, 0x0009, 0x0086, 0x007F, 0x0097, 0x008D, 0x008E, 0x000B, 0x000C, 0x000D, 0x000E, 0x000F,
    0x0010, 0x0011, 0x0012, 0x0013, 0x009D, 0x0085, 0x0008, 0x0087, 0x0018, 0x0019, 0x0092, 0x008F, 0x001C, 0x001D, 0x001E, 0x001F,
    0x0080, 0x0081, 0x0082, 0x0083, 0x0084, 0x000A, 0x0017, 0x001B, 0x0088, 0x0089, 0x008A, 0x008B, 0x008C, 0x0005, 0x0006, 0x0007,
    0x0090, 0x0091, 0x0016, 0x0093, 0x0094, 0x0095, 0x0096, 0x0004, 0x0098, 0x0099, 0x009A, 0x009B, 0x0014, 0x0015, 0x009E, 0x001A,
    0x0020, 0x00A0, 0x00E2, 0x00E4, 0x00E0, 0x00E1, 0x00E3, 0x00E5, 0x00E7, 0x00F1, 0x00A2, 0x002E, 0x003C, 0x0028, 0x002B, 0x007C,
    0x0026, 0x00E9, 0x00EA, 0x00EB, 0x00E8, 0x00ED, 0x00EE, 0x00EF, 0x00EC, 0x00DF, 0x0021, 0x0024, 0x002A, 0x0029, 0x003B, 0x00AC,
    0x002D, 0x002F, 0x00C2, 0x00C4, 0x00C0, 0x00C1, 0x00C3, 0x00C5, 0x00C7, 0x00D1, 0x00A6, 0x002C, 0x0025, 0x005F, 0x003E, 0x003F,
    0x00F8, 0x00C9, 0x00CA, 0x00CB, 0x00C8, 0x00CD, 0x00CE, 0x00CF, 0x00CC, 0x0060, 0x003A, 0x0023, 0x0040, 0x0027, 0x003D, 0x0022,
    0x00D8, 0x0061, 0x0062, 0x0063, 0x0064, 0x0065, 0x0066, 0x0067, 0x0068, 0x0069, 0x00AB, 0x00BB, 0x00F0, 0x00FD, 0x00FE, 0x00B1,
    0x00B0, 0x006A, 0x006B, 0x006C, 0x006D, 0x006E, 0x006F, 0x0070, 0x0071, 0x0072, 0x00AA, 0x00BA, 0x00E6, 0x00B8, 0x00C6, 0x00A4,
    0x00B5, 0x007E, 0x0073, 0x0074, 0x0075, 0x0076, 0x0077, 0x0078, 0x0079, 0x007A, 0x00A1, 0x00BF, 0x00D0, 0x00DD, 0x00DE, 0x00AE,
    0x005E, 0x00A3, 0x00A5, 0x00B7, 0x00A9, 0x00A7, 0x00B6, 0x00BC, 0x00BD, 0x00BE, 0x005B, 0x005D, 0x00AF, 0x00A8, 0x00B4, 0x00D7,
    0x007B, 0x0041, 0x0042, 0x0043, 0x0044, 0x0045, 0x0046, 0x0047, 0x0048, 0x0049, 0x00AD, 0x00F4, 0x00F6, 0x00F2, 0x00F3, 0x00F5,
    0x007D, 0x004A, 0x004B, 0x004C, 0x004D, 0x004E, 0x004F, 0x0050, 0x0051, 0x0052, 0x00B9, 0x00FB, 0x00FC, 0x00F9, 0x00FA, 0x00FF,
    0x005C, 0x00F7, 0x0053, 0x0054, 0x0055, 0x0056, 0x0057, 0x0058, 0x0059, 0x005A, 0x00B2, 0x00D4, 0x00D6, 0x00D2, 0x00D3, 0x00D5,
    0x0030, 0x0031, 0x0032, 0x0033, 0x0034, 0x0035, 0x0036, 0x0037, 0x0038, 0x0039, 0x00B3, 0x00DB, 0x00DC, 0x00D9, 0x00DA, 0x009F
};

static int looks_ebcdic_cobol(const unsigned char *source, size_t source_len)
{
    size_t sample_len = source_len < 8192 ? source_len : 8192;
    size_t ascii_text = 0;
    size_t ebcdic_text = 0;
    size_t ascii_spaces = 0;
    size_t ebcdic_spaces = 0;

    if (sample_len == 0) return 0;

    for (size_t i = 1; i < sample_len; i++) {
        if (source[i - 1] == 0x0D && source[i] == 0x25) {
            return 1;
        }
    }

    for (size_t i = 0; i < sample_len; i++) {
        unsigned char byte = source[i];
        if (byte == 0x20) ascii_spaces++;
        if (byte == 0x40) ebcdic_spaces++;
        if (byte == 9 || byte == 10 || byte == 13 || byte == 32 ||
            (byte >= 48 && byte <= 57) ||
            (byte >= 65 && byte <= 90) ||
            (byte >= 97 && byte <= 122)) {
            ascii_text++;
        }
        if (byte == 0x05 || byte == 0x15 || byte == 0x25 || byte == 0x40 ||
            (byte >= 0x81 && byte <= 0x89) ||
            (byte >= 0x91 && byte <= 0x99) ||
            (byte >= 0xA2 && byte <= 0xA9) ||
            (byte >= 0xC1 && byte <= 0xC9) ||
            (byte >= 0xD1 && byte <= 0xD9) ||
            (byte >= 0xE2 && byte <= 0xE9) ||
            (byte >= 0xF0 && byte <= 0xF9)) {
            ebcdic_text++;
        }
    }

    size_t min_ebcdic_spaces = ascii_spaces * 2;
    if (min_ebcdic_spaces < 4) min_ebcdic_spaces = 4;
    return ebcdic_text > ascii_text * 2 && ebcdic_spaces >= min_ebcdic_spaces;
}

static size_t utf8_codepoint_length(uint32_t codepoint)
{
    if (codepoint <= 0x7F) return 1;
    if (codepoint <= 0x7FF) return 2;
    if (codepoint <= 0xFFFF) return 3;
    return 4;
}

static void append_utf8_codepoint(unsigned char *output, size_t *offset, uint32_t codepoint)
{
    if (codepoint <= 0x7F) {
        output[(*offset)++] = (unsigned char)codepoint;
    } else if (codepoint <= 0x7FF) {
        output[(*offset)++] = (unsigned char)(0xC0 | (codepoint >> 6));
        output[(*offset)++] = (unsigned char)(0x80 | (codepoint & 0x3F));
    } else if (codepoint <= 0xFFFF) {
        output[(*offset)++] = (unsigned char)(0xE0 | (codepoint >> 12));
        output[(*offset)++] = (unsigned char)(0x80 | ((codepoint >> 6) & 0x3F));
        output[(*offset)++] = (unsigned char)(0x80 | (codepoint & 0x3F));
    } else {
        output[(*offset)++] = (unsigned char)(0xF0 | (codepoint >> 18));
        output[(*offset)++] = (unsigned char)(0x80 | ((codepoint >> 12) & 0x3F));
        output[(*offset)++] = (unsigned char)(0x80 | ((codepoint >> 6) & 0x3F));
        output[(*offset)++] = (unsigned char)(0x80 | (codepoint & 0x3F));
    }
}

static int decode_cp037_to_utf8(const unsigned char *source, size_t source_len, unsigned char **out_data, size_t *out_len)
{
    size_t capacity = 1;
    for (size_t i = 0; i < source_len; i++) {
        capacity += utf8_codepoint_length(CP037_TO_UNICODE[source[i]]);
    }

    unsigned char *output = malloc(capacity);
    if (!output) return TSMP_ERROR_OUT_OF_MEMORY;

    size_t offset = 0;
    for (size_t i = 0; i < source_len; i++) {
        append_utf8_codepoint(output, &offset, CP037_TO_UNICODE[source[i]]);
    }
    output[offset] = '\0';

    *out_data = output;
    *out_len = offset;
    return TSMP_OK;
}

static int slice_has_tab(const unsigned char *source, size_t start, size_t end)
{
    for (size_t i = start; i < end; i++) {
        if (source[i] == '\t') return 1;
    }
    return 0;
}

static int copy_cobol_parser_input(
    const unsigned char *source,
    size_t start,
    size_t end,
    unsigned char **out_data,
    size_t *out_len)
{
    size_t input_len = end > start ? end - start : 0;
    size_t capacity = input_len * 8 + 1;
    unsigned char *output = malloc(capacity);
    if (!output) return TSMP_ERROR_OUT_OF_MEMORY;

    size_t offset = 0;
    size_t column = 0;
    for (size_t i = start; i < end; i++) {
        unsigned char byte = source[i];
        if (byte == '\t') {
            size_t spaces = 8 - (column % 8);
            for (size_t s = 0; s < spaces; s++) {
                output[offset++] = ' ';
            }
            column += spaces;
            continue;
        }

        output[offset++] = byte;
        if (byte == '\r' || byte == '\n') {
            column = 0;
        } else {
            column++;
        }
    }
    output[offset] = '\0';

    *out_data = output;
    *out_len = offset;
    return TSMP_OK;
}

static int normalize_cobol_fixed_legacy(
    const unsigned char *source,
    size_t source_len,
    NormalizedSource *out_source)
{
    const unsigned char *working = source;
    size_t working_len = source_len;
    unsigned char *decoded = NULL;
    int status = TSMP_OK;
    size_t start = 0;
    size_t end = source_len;
    int changed = 0;

    if (looks_ebcdic_cobol(source, source_len)) {
        status = decode_cp037_to_utf8(source, source_len, &decoded, &working_len);
        if (status != TSMP_OK) return status;
        working = decoded;
        changed = 1;
    }

    end = working_len;

    if (working_len >= 3 &&
        working[0] == 0xEF &&
        working[1] == 0xBB &&
        working[2] == 0xBF) {
        start = 3;
        changed = 1;
    }

    while (end > start) {
        size_t candidate_end = trim_trailing_ascii_space(working, start, end);
        if (candidate_end > start &&
            (working[candidate_end - 1] == 0x1A ||
             working[candidate_end - 1] == 0x7F ||
             working[candidate_end - 1] == 0x00)) {
            end = candidate_end - 1;
            changed = 1;
            continue;
        }

        size_t line_start = candidate_end;
        while (line_start > start && working[line_start - 1] != '\n') {
            line_start--;
        }
        if (line_start < candidate_end &&
            is_cobol_legacy_trailer_line(working, line_start, candidate_end)) {
            end = line_start;
            changed = 1;
            continue;
        }

        break;
    }

    if (!changed && !slice_has_tab(working, start, end)) {
        free(decoded);
        return TSMP_OK;
    }

    size_t normalized_len = 0;
    unsigned char *copy = NULL;
    status = copy_cobol_parser_input(working, start, end, &copy, &normalized_len);
    free(decoded);
    if (status != TSMP_OK) return status;

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

size_t fastparse_language_count(void)
{
    return tsmp_language_count();
}

const char *fastparse_language_name(size_t index)
{
    return tsmp_language_name(index);
}

const char *fastparse_language_display_name(size_t index)
{
    return tsmp_language_display_name(index);
}

void fastparse_language_load_result_free(FastParseLanguageLoadResult *result)
{
    if (!result) return;
    free(result->language);
    free(result->display_name);
    free(result->error_message);
    language_load_result_init(result);
}
