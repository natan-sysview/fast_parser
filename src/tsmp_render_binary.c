#include "tsmp_render.h"

#include <string.h>

#define TSMP_BINARY_SCHEMA_VERSION 1

static int mp_u8(TsmpBuffer *buffer, unsigned char value)
{
    return tsmp_buffer_append_bytes(buffer, &value, 1);
}

static int mp_be16(TsmpBuffer *buffer, uint16_t value)
{
    unsigned char bytes[2] = {
        (unsigned char)((value >> 8) & 0xFFu),
        (unsigned char)(value & 0xFFu)
    };
    return tsmp_buffer_append_bytes(buffer, bytes, sizeof(bytes));
}

static int mp_be32(TsmpBuffer *buffer, uint32_t value)
{
    unsigned char bytes[4] = {
        (unsigned char)((value >> 24) & 0xFFu),
        (unsigned char)((value >> 16) & 0xFFu),
        (unsigned char)((value >> 8) & 0xFFu),
        (unsigned char)(value & 0xFFu)
    };
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
        (unsigned char)(value & 0xFFu)
    };
    return tsmp_buffer_append_bytes(buffer, bytes, sizeof(bytes));
}

static int mp_nil(TsmpBuffer *buffer)
{
    return mp_u8(buffer, 0xC0u);
}

static int mp_uint(TsmpBuffer *buffer, uint64_t value)
{
    if (value <= 0x7Fu) {
        return mp_u8(buffer, (unsigned char)value);
    }
    if (value <= 0xFFu) {
        return mp_u8(buffer, 0xCCu) && mp_u8(buffer, (unsigned char)value);
    }
    if (value <= 0xFFFFu) {
        return mp_u8(buffer, 0xCDu) && mp_be16(buffer, (uint16_t)value);
    }
    if (value <= 0xFFFFFFFFu) {
        return mp_u8(buffer, 0xCEu) && mp_be32(buffer, (uint32_t)value);
    }
    return mp_u8(buffer, 0xCFu) && mp_be64(buffer, value);
}

static int mp_map(TsmpBuffer *buffer, uint32_t count)
{
    if (count <= 15u) {
        return mp_u8(buffer, (unsigned char)(0x80u | count));
    }
    if (count <= 0xFFFFu) {
        return mp_u8(buffer, 0xDEu) && mp_be16(buffer, (uint16_t)count);
    }
    return mp_u8(buffer, 0xDFu) && mp_be32(buffer, count);
}

static int mp_array(TsmpBuffer *buffer, uint32_t count)
{
    if (count <= 15u) {
        return mp_u8(buffer, (unsigned char)(0x90u | count));
    }
    if (count <= 0xFFFFu) {
        return mp_u8(buffer, 0xDCu) && mp_be16(buffer, (uint16_t)count);
    }
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

static int mp_source_slice(TsmpBuffer *buffer, const TsmpRenderCtx *ctx, TSNode node)
{
    uint32_t start = ts_node_start_byte(node);
    uint32_t end = ts_node_end_byte(node);
    if (end < start) end = start;
    if ((size_t)start > ctx->source_len) start = (uint32_t)ctx->source_len;
    if ((size_t)end > ctx->source_len) end = (uint32_t)ctx->source_len;
    return mp_bin(buffer, ctx->source + start, (size_t)(end - start));
}

static uint32_t node_property_count(const TsmpRenderCtx *ctx)
{
    uint32_t count = 0;
    if (tsmp_has_field(ctx, TSMP_FIELD_ID)) count++;
    if (tsmp_has_field(ctx, TSMP_FIELD_PARENT_ID)) count++;
    if (tsmp_has_field(ctx, TSMP_FIELD_RULE)) count++;
    if (tsmp_has_field(ctx, TSMP_FIELD_TEXT)) count++;
    if (tsmp_has_field(ctx, TSMP_FIELD_RANGE)) count += 4;
    if (tsmp_has_field(ctx, TSMP_FIELD_BYTE_RANGE)) count += 2;
    if (tsmp_has_field(ctx, TSMP_FIELD_CHILD_COUNT)) count++;
    if (tsmp_has_field(ctx, TSMP_FIELD_CHILDREN)) count++;
    return count;
}

static uint32_t child_summary_count(const TsmpRenderCtx *ctx, TSNode node)
{
    uint32_t count = 0;
    uint32_t child_count = ts_node_child_count(node);
    for (uint32_t i = 0; i < child_count; i++) {
        TSNode child = ts_node_child(node, i);
        if (!ctx->options->include_tokens && !ts_node_is_named(child)) continue;
        count++;
    }
    return count;
}

static uint32_t child_property_count(const TsmpRenderCtx *ctx)
{
    uint32_t count = 0;
    if (ctx->fields == TSMP_FIELD_ALL || tsmp_has_field(ctx, TSMP_FIELD_RULE)) count++;
    if (ctx->fields == TSMP_FIELD_ALL || tsmp_has_field(ctx, TSMP_FIELD_TEXT)) count++;
    return count;
}

static int mp_children(TsmpBuffer *buffer, const TsmpRenderCtx *ctx, TSNode node)
{
    uint32_t child_count = ts_node_child_count(node);
    if (!mp_array(buffer, child_summary_count(ctx, node))) return 0;

    for (uint32_t i = 0; i < child_count; i++) {
        TSNode child = ts_node_child(node, i);
        if (!ctx->options->include_tokens && !ts_node_is_named(child)) continue;

        if (!mp_map(buffer, child_property_count(ctx))) return 0;
        if (ctx->fields == TSMP_FIELD_ALL || tsmp_has_field(ctx, TSMP_FIELD_RULE)) {
            if (!mp_key(buffer, "rule")) return 0;
            if (!mp_str(buffer, ts_node_is_named(child) ? ts_node_type(child) : "token")) return 0;
        }
        if (ctx->fields == TSMP_FIELD_ALL || tsmp_has_field(ctx, TSMP_FIELD_TEXT)) {
            if (!mp_key(buffer, "text")) return 0;
            if (!mp_source_slice(buffer, ctx, child)) return 0;
        }
    }

    return 1;
}

int tsmp_binary_begin(TsmpRenderCtx *ctx, size_t total_nodes)
{
    TsmpBuffer *buffer = &ctx->buffer;
    if (!mp_map(buffer, 5)) return 0;
    if (!mp_key(buffer, "format") || !mp_str(buffer, "tsmp-binary")) return 0;
    if (!mp_key(buffer, "schemaVersion") || !mp_uint(buffer, TSMP_BINARY_SCHEMA_VERSION)) return 0;
    if (!mp_key(buffer, "language") || !mp_str(buffer, ctx->options->language)) return 0;
    if (!mp_key(buffer, "nodes") || !mp_array(buffer, (uint32_t)total_nodes)) return 0;
    return 1;
}

int tsmp_binary_end(TsmpRenderCtx *ctx, size_t total_nodes)
{
    TsmpBuffer *buffer = &ctx->buffer;
    (void)total_nodes;
    if (!mp_key(buffer, "nodeCount")) return 0;
    return mp_uint(buffer, (uint64_t)ctx->node_count);
}

int tsmp_binary_node(TsmpRenderCtx *ctx, TSNode node, size_t node_id, size_t parent_id)
{
    TsmpBuffer *buffer = &ctx->buffer;
    TSPoint start_point = ts_node_start_point(node);
    TSPoint end_point = ts_node_end_point(node);

    if (!mp_map(buffer, node_property_count(ctx))) return 0;

    if (tsmp_has_field(ctx, TSMP_FIELD_ID)) {
        if (!mp_key(buffer, "id") || !mp_uint(buffer, (uint64_t)node_id)) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_PARENT_ID)) {
        if (!mp_key(buffer, "parentId")) return 0;
        if (parent_id == 0) {
            if (!mp_nil(buffer)) return 0;
        } else if (!mp_uint(buffer, (uint64_t)parent_id)) {
            return 0;
        }
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_RULE)) {
        if (!mp_key(buffer, "rule") || !mp_str(buffer, ts_node_type(node))) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_TEXT)) {
        if (!mp_key(buffer, "text") || !mp_source_slice(buffer, ctx, node)) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_RANGE)) {
        if (!mp_key(buffer, "startLine") || !mp_uint(buffer, start_point.row + 1)) return 0;
        if (!mp_key(buffer, "startColumn") || !mp_uint(buffer, start_point.column)) return 0;
        if (!mp_key(buffer, "endLine") || !mp_uint(buffer, end_point.row + 1)) return 0;
        if (!mp_key(buffer, "endColumn") || !mp_uint(buffer, end_point.column)) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_BYTE_RANGE)) {
        if (!mp_key(buffer, "startByte") || !mp_uint(buffer, ts_node_start_byte(node))) return 0;
        if (!mp_key(buffer, "endByte") || !mp_uint(buffer, ts_node_end_byte(node))) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_CHILD_COUNT)) {
        if (!mp_key(buffer, "childCount") || !mp_uint(buffer, ts_node_child_count(node))) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_CHILDREN)) {
        if (!mp_key(buffer, "children") || !mp_children(buffer, ctx, node)) return 0;
    }

    return 1;
}
