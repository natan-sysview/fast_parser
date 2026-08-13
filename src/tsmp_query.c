#include "../include/tsmp.h"

#include "tsmp_buffer.h"
#include "tsmp_languages.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tree_sitter/api.h>

#define TSMP_QUERY_BINARY_SCHEMA_VERSION 1
#define TSMP_QUERY_DEFAULT_FIELDS \
    (TSMP_FIELD_CAPTURE_NAME | TSMP_FIELD_RULE | TSMP_FIELD_TEXT | TSMP_FIELD_RANGE | TSMP_FIELD_BYTE_RANGE | TSMP_FIELD_PATTERN_INDEX)

typedef struct {
    const unsigned char *data;
    size_t length;
    unsigned char *owned;
} QuerySource;

typedef struct {
    size_t match_count;
    size_t capture_count;
} QueryCounts;

typedef struct {
    const unsigned char *source;
    size_t source_len;
    const char *language;
    unsigned int fields;
    size_t max_matches;
    size_t max_captures;
    size_t match_count;
    size_t capture_count;
    TsmpBuffer buffer;
} QueryRenderCtx;

static void query_result_init(TsmpResult *result)
{
    if (!result) return;
    result->status = TSMP_OK;
    result->data = NULL;
    result->length = 0;
    result->node_count = 0;
    result->error_message = NULL;
}

static char *query_copy_text(const char *value)
{
    const char *safe = value ? value : "";
    size_t len = strlen(safe);
    char *copy = malloc(len + 1);
    if (!copy) return NULL;
    memcpy(copy, safe, len + 1);
    return copy;
}

static int query_set_error(TsmpResult *result, int status, const char *message)
{
    if (!result) return status;
    result->status = status;
    result->data = NULL;
    result->length = 0;
    result->node_count = 0;
    result->error_message = query_copy_text(message);
    if (!result->error_message && message) {
        result->status = TSMP_ERROR_OUT_OF_MEMORY;
    }
    return result->status;
}

static int query_has_field(const QueryRenderCtx *ctx, unsigned int field)
{
    return (ctx->fields & field) != 0;
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

static int query_language_is(const char *language, const char *expected)
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
    QuerySource *out_source)
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

    if (working_len >= 3 && working[0] == 0xEF && working[1] == 0xBB && working[2] == 0xBF) {
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
        if (line_start < candidate_end && is_cobol_legacy_trailer_line(working, line_start, candidate_end)) {
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

static int normalize_query_source(
    const unsigned char *source,
    size_t source_len,
    const TsmpQueryOptions *options,
    QuerySource *out_source)
{
    out_source->data = source_len == 0 ? (const unsigned char *)"" : source;
    out_source->length = source_len;
    out_source->owned = NULL;

    if (options->normalization == TSMP_NORMALIZATION_NONE || source_len == 0) {
        return TSMP_OK;
    }
    if (options->normalization == TSMP_NORMALIZATION_COBOL_FIXED_LEGACY ||
        (options->normalization == TSMP_NORMALIZATION_AUTO_SAFE && query_language_is(options->language, "cobol"))) {
        return normalize_cobol_fixed_legacy(source, source_len, out_source);
    }
    return TSMP_OK;
}

static void query_source_free(QuerySource *source)
{
    if (!source) return;
    free(source->owned);
    source->data = NULL;
    source->length = 0;
    source->owned = NULL;
}

static int append_source_slice_json(TsmpBuffer *buffer, const QueryRenderCtx *ctx, TSNode node)
{
    uint32_t start = ts_node_start_byte(node);
    uint32_t end = ts_node_end_byte(node);
    if (end < start) end = start;
    if ((size_t)start > ctx->source_len) start = (uint32_t)ctx->source_len;
    if ((size_t)end > ctx->source_len) end = (uint32_t)ctx->source_len;
    return tsmp_buffer_append_json_bytes(buffer, ctx->source + start, (size_t)(end - start));
}

static int append_source_slice_csv(TsmpBuffer *buffer, const QueryRenderCtx *ctx, TSNode node)
{
    uint32_t start = ts_node_start_byte(node);
    uint32_t end = ts_node_end_byte(node);
    if (end < start) end = start;
    if ((size_t)start > ctx->source_len) start = (uint32_t)ctx->source_len;
    if ((size_t)end > ctx->source_len) end = (uint32_t)ctx->source_len;
    return tsmp_buffer_append_csv_bytes(buffer, ctx->source + start, (size_t)(end - start));
}

static int append_json_key(TsmpBuffer *buffer, const char *key, int *first)
{
    if (!*first && !tsmp_buffer_append(buffer, ",")) return 0;
    *first = 0;
    if (!tsmp_buffer_append(buffer, "\"")) return 0;
    if (!tsmp_buffer_append(buffer, key)) return 0;
    return tsmp_buffer_append(buffer, "\":");
}

static int append_csv_separator(TsmpBuffer *buffer, int *first)
{
    if (!*first && !tsmp_buffer_append(buffer, ",")) return 0;
    *first = 0;
    return 1;
}

static int capture_name(TSQuery *query, uint32_t index, const char **name, uint32_t *length)
{
    *name = ts_query_capture_name_for_id(query, index, length);
    return *name != NULL;
}

static uint32_t capture_property_count(const QueryRenderCtx *ctx)
{
    uint32_t count = 0;
    if (query_has_field(ctx, TSMP_FIELD_PATTERN_INDEX)) count++;
    if (query_has_field(ctx, TSMP_FIELD_CAPTURE_NAME)) count++;
    if (query_has_field(ctx, TSMP_FIELD_RULE)) count++;
    if (query_has_field(ctx, TSMP_FIELD_TEXT)) count++;
    if (query_has_field(ctx, TSMP_FIELD_RANGE)) count += 4;
    if (query_has_field(ctx, TSMP_FIELD_BYTE_RANGE)) count += 2;
    if (query_has_field(ctx, TSMP_FIELD_CHILD_COUNT)) count++;
    if (query_has_field(ctx, TSMP_FIELD_DIAGNOSTICS)) count += 3;
    return count;
}

static int render_json_capture(QueryRenderCtx *ctx, TSQuery *query, TSQueryMatch *match, TSQueryCapture capture)
{
    TsmpBuffer *buffer = &ctx->buffer;
    TSNode node = capture.node;
    TSPoint start_point = ts_node_start_point(node);
    TSPoint end_point = ts_node_end_point(node);
    const char *name = "";
    uint32_t name_len = 0;
    int first = 1;

    capture_name(query, capture.index, &name, &name_len);
    if (!tsmp_buffer_append(buffer, "{")) return 0;
    if (query_has_field(ctx, TSMP_FIELD_PATTERN_INDEX)) {
        if (!append_json_key(buffer, "patternIndex", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, match->pattern_index)) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_CAPTURE_NAME)) {
        if (!append_json_key(buffer, "name", &first)) return 0;
        if (!tsmp_buffer_append_json_bytes(buffer, (const unsigned char *)name, name_len)) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_RULE)) {
        if (!append_json_key(buffer, "rule", &first)) return 0;
        if (!tsmp_buffer_append_json_string(buffer, ts_node_type(node))) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_TEXT)) {
        if (!append_json_key(buffer, "text", &first)) return 0;
        if (!append_source_slice_json(buffer, ctx, node)) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_RANGE)) {
        if (!append_json_key(buffer, "startLine", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, start_point.row + 1)) return 0;
        if (!append_json_key(buffer, "startColumn", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, start_point.column)) return 0;
        if (!append_json_key(buffer, "endLine", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, end_point.row + 1)) return 0;
        if (!append_json_key(buffer, "endColumn", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, end_point.column)) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_BYTE_RANGE)) {
        if (!append_json_key(buffer, "startByte", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, ts_node_start_byte(node))) return 0;
        if (!append_json_key(buffer, "endByte", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, ts_node_end_byte(node))) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_CHILD_COUNT)) {
        if (!append_json_key(buffer, "childCount", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, ts_node_child_count(node))) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_DIAGNOSTICS)) {
        if (!append_json_key(buffer, "isError", &first)) return 0;
        if (!tsmp_buffer_append(buffer, ts_node_is_error(node) ? "true" : "false")) return 0;
        if (!append_json_key(buffer, "isMissing", &first)) return 0;
        if (!tsmp_buffer_append(buffer, ts_node_is_missing(node) ? "true" : "false")) return 0;
        if (!append_json_key(buffer, "hasError", &first)) return 0;
        if (!tsmp_buffer_append(buffer, ts_node_has_error(node) ? "true" : "false")) return 0;
    }
    return tsmp_buffer_append(buffer, "}");
}

static int render_json_query(
    QueryRenderCtx *ctx,
    TSQuery *query,
    TSQueryCursor *cursor,
    TSNode root)
{
    TSQueryMatch match;
    int first_match = 1;
    size_t emitted_matches = 0;
    size_t emitted_captures = 0;

    if (!tsmp_buffer_append(&ctx->buffer, "{\"language\":")) return 0;
    if (!tsmp_buffer_append_json_string(&ctx->buffer, ctx->language)) return 0;
    if (!tsmp_buffer_append(&ctx->buffer, ",\"matches\":[")) return 0;

    ts_query_cursor_exec(cursor, query, root);
    while (ts_query_cursor_next_match(cursor, &match)) {
        if (ctx->max_matches && emitted_matches >= ctx->max_matches) break;
        if (ctx->max_captures && emitted_captures >= ctx->max_captures) break;

        if (!first_match && !tsmp_buffer_append(&ctx->buffer, ",")) return 0;
        first_match = 0;
        emitted_matches++;
        ctx->match_count++;

        if (!tsmp_buffer_append(&ctx->buffer, "{\"patternIndex\":")) return 0;
        if (!tsmp_buffer_append_u32(&ctx->buffer, match.pattern_index)) return 0;
        if (!tsmp_buffer_append(&ctx->buffer, ",\"captures\":[")) return 0;
        int first_capture = 1;
        for (uint16_t i = 0; i < match.capture_count; i++) {
            if (ctx->max_captures && emitted_captures >= ctx->max_captures) break;
            if (!first_capture && !tsmp_buffer_append(&ctx->buffer, ",")) return 0;
            first_capture = 0;
            if (!render_json_capture(ctx, query, &match, match.captures[i])) return 0;
            emitted_captures++;
            ctx->capture_count++;
        }
        if (!tsmp_buffer_append(&ctx->buffer, "]}")) return 0;
    }

    if (!tsmp_buffer_append(&ctx->buffer, "],\"matchCount\":")) return 0;
    if (!tsmp_buffer_append_size(&ctx->buffer, ctx->match_count)) return 0;
    if (!tsmp_buffer_append(&ctx->buffer, ",\"captureCount\":")) return 0;
    if (!tsmp_buffer_append_size(&ctx->buffer, ctx->capture_count)) return 0;
    return tsmp_buffer_append(&ctx->buffer, "}");
}

static int render_csv_query(
    QueryRenderCtx *ctx,
    TSQuery *query,
    TSQueryCursor *cursor,
    TSNode root)
{
    TSQueryMatch match;
    size_t emitted_matches = 0;
    size_t emitted_captures = 0;
    int first = 1;

    if (query_has_field(ctx, TSMP_FIELD_PATTERN_INDEX)) {
        if (!append_csv_separator(&ctx->buffer, &first) || !tsmp_buffer_append(&ctx->buffer, "pattern_index")) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_CAPTURE_NAME)) {
        if (!append_csv_separator(&ctx->buffer, &first) || !tsmp_buffer_append(&ctx->buffer, "capture_name")) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_RULE)) {
        if (!append_csv_separator(&ctx->buffer, &first) || !tsmp_buffer_append(&ctx->buffer, "rule")) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_TEXT)) {
        if (!append_csv_separator(&ctx->buffer, &first) || !tsmp_buffer_append(&ctx->buffer, "text")) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_RANGE)) {
        if (!append_csv_separator(&ctx->buffer, &first) ||
            !tsmp_buffer_append(&ctx->buffer, "start_line,start_column,end_line,end_column")) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_BYTE_RANGE)) {
        if (!append_csv_separator(&ctx->buffer, &first) ||
            !tsmp_buffer_append(&ctx->buffer, "start_byte,end_byte")) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_CHILD_COUNT)) {
        if (!append_csv_separator(&ctx->buffer, &first) || !tsmp_buffer_append(&ctx->buffer, "child_count")) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_DIAGNOSTICS)) {
        if (!append_csv_separator(&ctx->buffer, &first) ||
            !tsmp_buffer_append(&ctx->buffer, "is_error,is_missing,has_error")) return 0;
    }
    if (!tsmp_buffer_append(&ctx->buffer, "\n")) return 0;

    ts_query_cursor_exec(cursor, query, root);
    while (ts_query_cursor_next_match(cursor, &match)) {
        if (ctx->max_matches && emitted_matches >= ctx->max_matches) break;
        if (ctx->max_captures && emitted_captures >= ctx->max_captures) break;
        emitted_matches++;
        ctx->match_count++;

        for (uint16_t i = 0; i < match.capture_count; i++) {
            TSNode node = match.captures[i].node;
            TSPoint start_point = ts_node_start_point(node);
            TSPoint end_point = ts_node_end_point(node);
            const char *name = "";
            uint32_t name_len = 0;
            first = 1;

            if (ctx->max_captures && emitted_captures >= ctx->max_captures) break;
            capture_name(query, match.captures[i].index, &name, &name_len);
            if (query_has_field(ctx, TSMP_FIELD_PATTERN_INDEX)) {
                if (!append_csv_separator(&ctx->buffer, &first) || !tsmp_buffer_append_u32(&ctx->buffer, match.pattern_index)) return 0;
            }
            if (query_has_field(ctx, TSMP_FIELD_CAPTURE_NAME)) {
                if (!append_csv_separator(&ctx->buffer, &first) ||
                    !tsmp_buffer_append_csv_bytes(&ctx->buffer, (const unsigned char *)name, name_len)) return 0;
            }
            if (query_has_field(ctx, TSMP_FIELD_RULE)) {
                const char *rule = ts_node_type(node);
                if (!append_csv_separator(&ctx->buffer, &first) ||
                    !tsmp_buffer_append_csv_bytes(&ctx->buffer, (const unsigned char *)rule, strlen(rule))) return 0;
            }
            if (query_has_field(ctx, TSMP_FIELD_TEXT)) {
                if (!append_csv_separator(&ctx->buffer, &first) || !append_source_slice_csv(&ctx->buffer, ctx, node)) return 0;
            }
            if (query_has_field(ctx, TSMP_FIELD_RANGE)) {
                if (!append_csv_separator(&ctx->buffer, &first) ||
                    !tsmp_buffer_append_u32(&ctx->buffer, start_point.row + 1) ||
                    !tsmp_buffer_append(&ctx->buffer, ",") ||
                    !tsmp_buffer_append_u32(&ctx->buffer, start_point.column) ||
                    !tsmp_buffer_append(&ctx->buffer, ",") ||
                    !tsmp_buffer_append_u32(&ctx->buffer, end_point.row + 1) ||
                    !tsmp_buffer_append(&ctx->buffer, ",") ||
                    !tsmp_buffer_append_u32(&ctx->buffer, end_point.column)) return 0;
            }
            if (query_has_field(ctx, TSMP_FIELD_BYTE_RANGE)) {
                if (!append_csv_separator(&ctx->buffer, &first) ||
                    !tsmp_buffer_append_u32(&ctx->buffer, ts_node_start_byte(node)) ||
                    !tsmp_buffer_append(&ctx->buffer, ",") ||
                    !tsmp_buffer_append_u32(&ctx->buffer, ts_node_end_byte(node))) return 0;
            }
            if (query_has_field(ctx, TSMP_FIELD_CHILD_COUNT)) {
                if (!append_csv_separator(&ctx->buffer, &first) ||
                    !tsmp_buffer_append_u32(&ctx->buffer, ts_node_child_count(node))) return 0;
            }
            if (query_has_field(ctx, TSMP_FIELD_DIAGNOSTICS)) {
                if (!append_csv_separator(&ctx->buffer, &first) ||
                    !tsmp_buffer_append(&ctx->buffer, ts_node_is_error(node) ? "1" : "0") ||
                    !tsmp_buffer_append(&ctx->buffer, ",") ||
                    !tsmp_buffer_append(&ctx->buffer, ts_node_is_missing(node) ? "1" : "0") ||
                    !tsmp_buffer_append(&ctx->buffer, ",") ||
                    !tsmp_buffer_append(&ctx->buffer, ts_node_has_error(node) ? "1" : "0")) return 0;
            }
            if (!tsmp_buffer_append(&ctx->buffer, "\n")) return 0;
            emitted_captures++;
            ctx->capture_count++;
        }
    }
    return 1;
}

static int mp_u8(TsmpBuffer *buffer, unsigned char value)
{
    return tsmp_buffer_append_bytes(buffer, &value, 1);
}

static int mp_be16(TsmpBuffer *buffer, uint16_t value)
{
    unsigned char bytes[2] = {(unsigned char)((value >> 8) & 0xFFu), (unsigned char)(value & 0xFFu)};
    return tsmp_buffer_append_bytes(buffer, bytes, sizeof(bytes));
}

static int mp_be32(TsmpBuffer *buffer, uint32_t value)
{
    unsigned char bytes[4] = {
        (unsigned char)((value >> 24) & 0xFFu),
        (unsigned char)((value >> 16) & 0xFFu),
        (unsigned char)((value >> 8) & 0xFFu),
        (unsigned char)(value & 0xFFu)};
    return tsmp_buffer_append_bytes(buffer, bytes, sizeof(bytes));
}

static int mp_be64(TsmpBuffer *buffer, uint64_t value)
{
    unsigned char bytes[8] = {
        (unsigned char)((value >> 56) & 0xFFu),
        (unsigned char)((value >> 48) & 0xFFu),
        (unsigned char)((value >> 40) & 0xFFu),
        (unsigned char)((value >> 32) & 0xFFu),
        (unsigned char)((value >> 24) & 0xFFu),
        (unsigned char)((value >> 16) & 0xFFu),
        (unsigned char)((value >> 8) & 0xFFu),
        (unsigned char)(value & 0xFFu)};
    return tsmp_buffer_append_bytes(buffer, bytes, sizeof(bytes));
}

static int mp_bool(TsmpBuffer *buffer, int value)
{
    return mp_u8(buffer, value ? 0xC3u : 0xC2u);
}

static int mp_uint(TsmpBuffer *buffer, uint64_t value)
{
    if (value <= 0x7Fu) return mp_u8(buffer, (unsigned char)value);
    if (value <= 0xFFu) return mp_u8(buffer, 0xCCu) && mp_u8(buffer, (unsigned char)value);
    if (value <= 0xFFFFu) return mp_u8(buffer, 0xCDu) && mp_be16(buffer, (uint16_t)value);
    if (value <= 0xFFFFFFFFu) return mp_u8(buffer, 0xCEu) && mp_be32(buffer, (uint32_t)value);
    return mp_u8(buffer, 0xCFu) && mp_be64(buffer, value);
}

static int mp_map(TsmpBuffer *buffer, uint32_t count)
{
    if (count <= 15u) return mp_u8(buffer, (unsigned char)(0x80u | count));
    if (count <= 0xFFFFu) return mp_u8(buffer, 0xDEu) && mp_be16(buffer, (uint16_t)count);
    return mp_u8(buffer, 0xDFu) && mp_be32(buffer, count);
}

static int mp_array(TsmpBuffer *buffer, uint32_t count)
{
    if (count <= 15u) return mp_u8(buffer, (unsigned char)(0x90u | count));
    if (count <= 0xFFFFu) return mp_u8(buffer, 0xDCu) && mp_be16(buffer, (uint16_t)count);
    return mp_u8(buffer, 0xDDu) && mp_be32(buffer, count);
}

static int mp_str_bytes(TsmpBuffer *buffer, const unsigned char *data, size_t len)
{
    if (len <= 31u) {
        if (!mp_u8(buffer, (unsigned char)(0xA0u | len))) return 0;
    } else if (len <= 0xFFu) {
        if (!mp_u8(buffer, 0xD9u) || !mp_u8(buffer, (unsigned char)len)) return 0;
    } else if (len <= 0xFFFFu) {
        if (!mp_u8(buffer, 0xDAu) || !mp_be16(buffer, (uint16_t)len)) return 0;
    } else {
        if (!mp_u8(buffer, 0xDBu) || !mp_be32(buffer, (uint32_t)len)) return 0;
    }
    return tsmp_buffer_append_bytes(buffer, data, len);
}

static int mp_str(TsmpBuffer *buffer, const char *value)
{
    const char *safe = value ? value : "";
    return mp_str_bytes(buffer, (const unsigned char *)safe, strlen(safe));
}

static int mp_bin(TsmpBuffer *buffer, const unsigned char *data, size_t len)
{
    if (len <= 0xFFu) {
        if (!mp_u8(buffer, 0xC4u) || !mp_u8(buffer, (unsigned char)len)) return 0;
    } else if (len <= 0xFFFFu) {
        if (!mp_u8(buffer, 0xC5u) || !mp_be16(buffer, (uint16_t)len)) return 0;
    } else {
        if (!mp_u8(buffer, 0xC6u) || !mp_be32(buffer, (uint32_t)len)) return 0;
    }
    return tsmp_buffer_append_bytes(buffer, data, len);
}

static int mp_key(TsmpBuffer *buffer, const char *key)
{
    return mp_str(buffer, key);
}

static int mp_source_slice(TsmpBuffer *buffer, const QueryRenderCtx *ctx, TSNode node)
{
    uint32_t start = ts_node_start_byte(node);
    uint32_t end = ts_node_end_byte(node);
    if (end < start) end = start;
    if ((size_t)start > ctx->source_len) start = (uint32_t)ctx->source_len;
    if ((size_t)end > ctx->source_len) end = (uint32_t)ctx->source_len;
    return mp_bin(buffer, ctx->source + start, (size_t)(end - start));
}

static QueryCounts count_query(TSQuery *query, TSQueryCursor *cursor, TSNode root, size_t max_matches, size_t max_captures)
{
    TSQueryMatch match;
    QueryCounts counts;
    memset(&counts, 0, sizeof(counts));
    ts_query_cursor_exec(cursor, query, root);
    while (ts_query_cursor_next_match(cursor, &match)) {
        if (max_matches && counts.match_count >= max_matches) break;
        if (max_captures && counts.capture_count >= max_captures) break;
        counts.match_count++;
        for (uint16_t i = 0; i < match.capture_count; i++) {
            if (max_captures && counts.capture_count >= max_captures) break;
            counts.capture_count++;
        }
    }
    return counts;
}

static int render_binary_capture(QueryRenderCtx *ctx, TSQuery *query, TSQueryMatch *match, TSQueryCapture capture)
{
    TSNode node = capture.node;
    TSPoint start_point = ts_node_start_point(node);
    TSPoint end_point = ts_node_end_point(node);
    const char *name = "";
    uint32_t name_len = 0;
    capture_name(query, capture.index, &name, &name_len);

    if (!mp_map(&ctx->buffer, capture_property_count(ctx))) return 0;
    if (query_has_field(ctx, TSMP_FIELD_PATTERN_INDEX)) {
        if (!mp_key(&ctx->buffer, "patternIndex") || !mp_uint(&ctx->buffer, match->pattern_index)) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_CAPTURE_NAME)) {
        if (!mp_key(&ctx->buffer, "name") || !mp_str_bytes(&ctx->buffer, (const unsigned char *)name, name_len)) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_RULE)) {
        if (!mp_key(&ctx->buffer, "rule") || !mp_str(&ctx->buffer, ts_node_type(node))) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_TEXT)) {
        if (!mp_key(&ctx->buffer, "text") || !mp_source_slice(&ctx->buffer, ctx, node)) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_RANGE)) {
        if (!mp_key(&ctx->buffer, "startLine") || !mp_uint(&ctx->buffer, start_point.row + 1)) return 0;
        if (!mp_key(&ctx->buffer, "startColumn") || !mp_uint(&ctx->buffer, start_point.column)) return 0;
        if (!mp_key(&ctx->buffer, "endLine") || !mp_uint(&ctx->buffer, end_point.row + 1)) return 0;
        if (!mp_key(&ctx->buffer, "endColumn") || !mp_uint(&ctx->buffer, end_point.column)) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_BYTE_RANGE)) {
        if (!mp_key(&ctx->buffer, "startByte") || !mp_uint(&ctx->buffer, ts_node_start_byte(node))) return 0;
        if (!mp_key(&ctx->buffer, "endByte") || !mp_uint(&ctx->buffer, ts_node_end_byte(node))) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_CHILD_COUNT)) {
        if (!mp_key(&ctx->buffer, "childCount") || !mp_uint(&ctx->buffer, ts_node_child_count(node))) return 0;
    }
    if (query_has_field(ctx, TSMP_FIELD_DIAGNOSTICS)) {
        if (!mp_key(&ctx->buffer, "isError") || !mp_bool(&ctx->buffer, ts_node_is_error(node))) return 0;
        if (!mp_key(&ctx->buffer, "isMissing") || !mp_bool(&ctx->buffer, ts_node_is_missing(node))) return 0;
        if (!mp_key(&ctx->buffer, "hasError") || !mp_bool(&ctx->buffer, ts_node_has_error(node))) return 0;
    }
    return 1;
}

static int render_binary_query(
    QueryRenderCtx *ctx,
    TSQuery *query,
    TSQueryCursor *cursor,
    TSNode root,
    QueryCounts counts)
{
    TSQueryMatch match;
    size_t emitted_matches = 0;
    size_t emitted_captures = 0;

    if (!mp_map(&ctx->buffer, 6)) return 0;
    if (!mp_key(&ctx->buffer, "format") || !mp_str(&ctx->buffer, "fastparse-query-binary")) return 0;
    if (!mp_key(&ctx->buffer, "schemaVersion") || !mp_uint(&ctx->buffer, TSMP_QUERY_BINARY_SCHEMA_VERSION)) return 0;
    if (!mp_key(&ctx->buffer, "language") || !mp_str(&ctx->buffer, ctx->language)) return 0;
    if (!mp_key(&ctx->buffer, "matchCount") || !mp_uint(&ctx->buffer, counts.match_count)) return 0;
    if (!mp_key(&ctx->buffer, "captureCount") || !mp_uint(&ctx->buffer, counts.capture_count)) return 0;
    if (!mp_key(&ctx->buffer, "matches") || !mp_array(&ctx->buffer, (uint32_t)counts.match_count)) return 0;

    ts_query_cursor_exec(cursor, query, root);
    while (ts_query_cursor_next_match(cursor, &match)) {
        if (ctx->max_matches && emitted_matches >= ctx->max_matches) break;
        if (ctx->max_captures && emitted_captures >= ctx->max_captures) break;
        emitted_matches++;
        ctx->match_count++;

        uint32_t capture_count = 0;
        for (uint16_t i = 0; i < match.capture_count; i++) {
            if (ctx->max_captures && emitted_captures + capture_count >= ctx->max_captures) break;
            capture_count++;
        }

        if (!mp_map(&ctx->buffer, 2)) return 0;
        if (!mp_key(&ctx->buffer, "patternIndex") || !mp_uint(&ctx->buffer, match.pattern_index)) return 0;
        if (!mp_key(&ctx->buffer, "captures") || !mp_array(&ctx->buffer, capture_count)) return 0;
        for (uint16_t i = 0; i < capture_count; i++) {
            if (!render_binary_capture(ctx, query, &match, match.captures[i])) return 0;
            emitted_captures++;
            ctx->capture_count++;
        }
    }
    return 1;
}

static int finish_buffer(QueryRenderCtx *ctx, TsmpResult *out_result)
{
    size_t output_len = ctx->buffer.len;
    out_result->status = TSMP_OK;
    out_result->data = (unsigned char *)tsmp_buffer_take(&ctx->buffer);
    out_result->length = output_len;
    out_result->node_count = ctx->capture_count;
    out_result->error_message = NULL;
    return TSMP_OK;
}

static int render_query_result(
    const QuerySource *source,
    const TsmpQueryOptions *options,
    TSQuery *query,
    TSTree *tree,
    TsmpResult *out_result)
{
    TSQueryCursor *cursor = ts_query_cursor_new();
    if (!cursor) return query_set_error(out_result, TSMP_ERROR_OUT_OF_MEMORY, "Could not allocate Tree-sitter query cursor.");

    QueryRenderCtx ctx;
    memset(&ctx, 0, sizeof(ctx));
    ctx.source = source->data;
    ctx.source_len = source->length;
    ctx.language = options->language;
    ctx.fields = options->fields ? options->fields : TSMP_QUERY_DEFAULT_FIELDS;
    if (options->include_pattern) ctx.fields |= TSMP_FIELD_PATTERN_INDEX;
    ctx.max_matches = options->max_matches;
    ctx.max_captures = options->max_captures;
    TSNode root = ts_tree_root_node(tree);

    if (options->format == TSMP_FORMAT_STATS) {
        QueryCounts counts = count_query(query, cursor, root, ctx.max_matches, ctx.max_captures);
        out_result->status = TSMP_OK;
        out_result->data = NULL;
        out_result->length = counts.match_count;
        out_result->node_count = counts.capture_count;
        out_result->error_message = NULL;
        ts_query_cursor_delete(cursor);
        return TSMP_OK;
    }

    if (!tsmp_buffer_init(&ctx.buffer, 4096)) {
        ts_query_cursor_delete(cursor);
        return query_set_error(out_result, TSMP_ERROR_OUT_OF_MEMORY, "Could not allocate query output buffer.");
    }

    int ok = 0;
    if (options->format == TSMP_FORMAT_JSON) {
        ok = render_json_query(&ctx, query, cursor, root);
    } else if (options->format == TSMP_FORMAT_CSV) {
        ok = render_csv_query(&ctx, query, cursor, root);
    } else if (options->format == TSMP_FORMAT_BINARY) {
        QueryCounts counts = count_query(query, cursor, root, ctx.max_matches, ctx.max_captures);
        ok = render_binary_query(&ctx, query, cursor, root, counts);
    } else {
        tsmp_buffer_free(&ctx.buffer);
        ts_query_cursor_delete(cursor);
        return query_set_error(out_result, TSMP_ERROR_UNSUPPORTED_FORMAT, "Unsupported query output format.");
    }

    ts_query_cursor_delete(cursor);
    if (!ok) {
        tsmp_buffer_free(&ctx.buffer);
        return query_set_error(out_result, TSMP_ERROR_OUT_OF_MEMORY, "Failed to render query result.");
    }
    return finish_buffer(&ctx, out_result);
}

static const char *query_error_name(TSQueryError error)
{
    switch (error) {
        case TSQueryErrorSyntax: return "syntax";
        case TSQueryErrorNodeType: return "node_type";
        case TSQueryErrorField: return "field";
        case TSQueryErrorCapture: return "capture";
        case TSQueryErrorStructure: return "structure";
        case TSQueryErrorLanguage: return "language";
        default: return "unknown";
    }
}

int tsmp_query(
    const unsigned char *source,
    size_t source_len,
    const unsigned char *query_text,
    size_t query_len,
    const TsmpQueryOptions *options,
    TsmpResult *out_result)
{
    if (!out_result) return TSMP_ERROR_INVALID_ARGUMENT;
    query_result_init(out_result);

    if ((source_len > 0 && !source) || (query_len > 0 && !query_text) || !options || !options->language) {
        return query_set_error(out_result, TSMP_ERROR_INVALID_ARGUMENT, "source, query, options, and options.language are required.");
    }
    if (query_len == 0) {
        return query_set_error(out_result, TSMP_ERROR_INVALID_ARGUMENT, "query must not be empty.");
    }
    if (query_len > UINT32_MAX || source_len > UINT32_MAX) {
        return query_set_error(out_result, TSMP_ERROR_INVALID_ARGUMENT, "source_len and query_len must fit Tree-sitter uint32 inputs.");
    }
    if (options->format != TSMP_FORMAT_JSON &&
        options->format != TSMP_FORMAT_CSV &&
        options->format != TSMP_FORMAT_STATS &&
        options->format != TSMP_FORMAT_BINARY) {
        return query_set_error(out_result, TSMP_ERROR_UNSUPPORTED_FORMAT, "Unsupported query output format.");
    }
    if (options->normalization != TSMP_NORMALIZATION_AUTO_SAFE &&
        options->normalization != TSMP_NORMALIZATION_NONE &&
        options->normalization != TSMP_NORMALIZATION_COBOL_FIXED_LEGACY) {
        return query_set_error(out_result, TSMP_ERROR_INVALID_ARGUMENT, "Unsupported normalization mode.");
    }

    const TSLanguage *language = tsmp_find_language(options->language);
    if (!language) {
        return query_set_error(out_result, TSMP_ERROR_UNSUPPORTED_LANGUAGE, "Unsupported language.");
    }

    QuerySource normalized_source;
    int normalize_status = normalize_query_source(source, source_len, options, &normalized_source);
    if (normalize_status != TSMP_OK) {
        return query_set_error(out_result, normalize_status, "Failed to normalize source.");
    }

    TSParser *parser = ts_parser_new();
    if (!parser) {
        query_source_free(&normalized_source);
        return query_set_error(out_result, TSMP_ERROR_OUT_OF_MEMORY, "Could not allocate Tree-sitter parser.");
    }
    if (!ts_parser_set_language(parser, language)) {
        ts_parser_delete(parser);
        query_source_free(&normalized_source);
        return query_set_error(out_result, TSMP_ERROR_PARSE_FAILED, "Grammar is incompatible with the Tree-sitter runtime.");
    }

    const char *parse_source = normalized_source.length == 0 ? "" : (const char *)normalized_source.data;
    TSTree *tree = ts_parser_parse_string(parser, NULL, parse_source, (uint32_t)normalized_source.length);
    if (!tree) {
        ts_parser_delete(parser);
        query_source_free(&normalized_source);
        return query_set_error(out_result, TSMP_ERROR_PARSE_FAILED, "Tree-sitter parse failed.");
    }

    uint32_t error_offset = 0;
    TSQueryError query_error = TSQueryErrorNone;
    TSQuery *query = ts_query_new(language, (const char *)query_text, (uint32_t)query_len, &error_offset, &query_error);
    if (!query) {
        char message[256];
        snprintf(message, sizeof(message), "Tree-sitter query compile failed: %s at byte offset %u.", query_error_name(query_error), error_offset);
        ts_tree_delete(tree);
        ts_parser_delete(parser);
        query_source_free(&normalized_source);
        return query_set_error(out_result, TSMP_ERROR_QUERY_COMPILE, message);
    }

    int status = render_query_result(&normalized_source, options, query, tree, out_result);
    if (status != TSMP_OK && !out_result->error_message) {
        query_set_error(out_result, status, "Failed to execute query.");
    }

    ts_query_delete(query);
    ts_tree_delete(tree);
    ts_parser_delete(parser);
    query_source_free(&normalized_source);
    return out_result->status;
}

int fastparse_query(
    const unsigned char *source,
    size_t source_len,
    const unsigned char *query,
    size_t query_len,
    const TsmpQueryOptions *options,
    TsmpResult *out_result)
{
    return tsmp_query(source, source_len, query, query_len, options, out_result);
}
