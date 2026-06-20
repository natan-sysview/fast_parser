#include "tsmp_render.h"

#include <string.h>

static int append_json_key(TsmpBuffer *buffer, const char *key, int *first)
{
    if (!*first && !tsmp_buffer_append(buffer, ",")) return 0;
    *first = 0;
    if (!tsmp_buffer_append(buffer, "\"")) return 0;
    if (!tsmp_buffer_append(buffer, key)) return 0;
    return tsmp_buffer_append(buffer, "\":");
}

int tsmp_json_begin(TsmpRenderCtx *ctx)
{
    if (!tsmp_buffer_append(&ctx->buffer, "{\"language\":")) return 0;
    if (!tsmp_buffer_append_json_string(&ctx->buffer, ctx->options->language)) return 0;
    return tsmp_buffer_append(&ctx->buffer, ",\"nodes\":[");
}

int tsmp_json_end(TsmpRenderCtx *ctx)
{
    if (!tsmp_buffer_append(&ctx->buffer, "],\"nodeCount\":")) return 0;
    if (!tsmp_buffer_append_size(&ctx->buffer, ctx->node_count)) return 0;
    return tsmp_buffer_append(&ctx->buffer, "}");
}

int tsmp_json_children(TsmpBuffer *buffer, const TsmpRenderCtx *ctx, TSNode node)
{
    if (!tsmp_buffer_append(buffer, "[")) return 0;

    uint32_t child_count = ts_node_child_count(node);
    int first = 1;
    for (uint32_t i = 0; i < child_count; i++) {
        TSNode child = ts_node_child(node, i);
        if (!ctx->options->include_tokens && !ts_node_is_named(child)) continue;

        if (!first && !tsmp_buffer_append(buffer, ",")) return 0;
        first = 0;

        int prop_first = 1;
        if (!tsmp_buffer_append(buffer, "{")) return 0;
        if (ctx->fields == TSMP_FIELD_ALL || tsmp_has_field(ctx, TSMP_FIELD_RULE)) {
            if (!append_json_key(buffer, "rule", &prop_first)) return 0;
            if (!tsmp_buffer_append_json_string(buffer, ts_node_is_named(child) ? ts_node_type(child) : "token")) return 0;
        }
        if (ctx->fields == TSMP_FIELD_ALL || tsmp_has_field(ctx, TSMP_FIELD_TEXT)) {
            if (!append_json_key(buffer, "text", &prop_first)) return 0;
            if (!tsmp_append_source_slice_json(buffer, ctx, child)) return 0;
        }
        if (!tsmp_buffer_append(buffer, "}")) return 0;
    }

    return tsmp_buffer_append(buffer, "]");
}

int tsmp_json_node(TsmpRenderCtx *ctx, TSNode node, size_t node_id, size_t parent_id)
{
    TsmpBuffer *buffer = &ctx->buffer;
    TSPoint start_point = ts_node_start_point(node);
    TSPoint end_point = ts_node_end_point(node);
    int first = 1;

    if (ctx->node_count > 0 && !tsmp_buffer_append(buffer, ",")) return 0;
    if (!tsmp_buffer_append(buffer, "{")) return 0;

    if (tsmp_has_field(ctx, TSMP_FIELD_ID)) {
        if (!append_json_key(buffer, "id", &first)) return 0;
        if (!tsmp_buffer_append_size(buffer, node_id)) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_PARENT_ID)) {
        if (!append_json_key(buffer, "parentId", &first)) return 0;
        if (parent_id == 0) {
            if (!tsmp_buffer_append(buffer, "null")) return 0;
        } else if (!tsmp_buffer_append_size(buffer, parent_id)) {
            return 0;
        }
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_RULE)) {
        if (!append_json_key(buffer, "rule", &first)) return 0;
        if (!tsmp_buffer_append_json_string(buffer, ts_node_type(node))) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_TEXT)) {
        if (!append_json_key(buffer, "text", &first)) return 0;
        if (!tsmp_append_source_slice_json(buffer, ctx, node)) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_RANGE)) {
        if (!append_json_key(buffer, "startLine", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, start_point.row + 1)) return 0;
        if (!append_json_key(buffer, "startColumn", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, start_point.column)) return 0;
        if (!append_json_key(buffer, "endLine", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, end_point.row + 1)) return 0;
        if (!append_json_key(buffer, "endColumn", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, end_point.column)) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_BYTE_RANGE)) {
        if (!append_json_key(buffer, "startByte", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, ts_node_start_byte(node))) return 0;
        if (!append_json_key(buffer, "endByte", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, ts_node_end_byte(node))) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_CHILD_COUNT)) {
        if (!append_json_key(buffer, "childCount", &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, ts_node_child_count(node))) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_CHILDREN)) {
        if (!append_json_key(buffer, "children", &first)) return 0;
        if (!tsmp_json_children(buffer, ctx, node)) return 0;
    }

    return tsmp_buffer_append(buffer, "}");
}
