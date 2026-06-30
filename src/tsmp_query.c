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

static int normalize_cobol_fixed_legacy(
    const unsigned char *source,
    size_t source_len,
    QuerySource *out_source)
{
    size_t start = 0;
    size_t end = source_len;
    int changed = 0;

    if (source_len >= 3 && source[0] == 0xEF && source[1] == 0xBB && source[2] == 0xBF) {
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
        if (line_start < candidate_end && is_cobol_legacy_trailer_line(source, line_start, candidate_end)) {
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
