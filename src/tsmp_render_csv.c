#include "tsmp_render.h"

#include <string.h>

static int append_separator(TsmpBuffer *buffer, int *first)
{
    if (!*first && !tsmp_buffer_append(buffer, ",")) return 0;
    *first = 0;
    return 1;
}

static int append_header_field(TsmpRenderCtx *ctx, int *first, unsigned int field, const char *name)
{
    if (!tsmp_has_field(ctx, field)) return 1;
    if (!append_separator(&ctx->buffer, first)) return 0;
    return tsmp_buffer_append(&ctx->buffer, name);
}

int tsmp_csv_begin(TsmpRenderCtx *ctx)
{
    int first = 1;
    if (!append_header_field(ctx, &first, TSMP_FIELD_ID, "id")) return 0;
    if (!append_header_field(ctx, &first, TSMP_FIELD_PARENT_ID, "parent_id")) return 0;
    if (!append_header_field(ctx, &first, TSMP_FIELD_RULE, "rule")) return 0;
    if (!append_header_field(ctx, &first, TSMP_FIELD_TEXT, "text")) return 0;

    if (tsmp_has_field(ctx, TSMP_FIELD_RANGE)) {
        if (!append_separator(&ctx->buffer, &first)) return 0;
        if (!tsmp_buffer_append(&ctx->buffer, "start_line,start_column,end_line,end_column")) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_BYTE_RANGE)) {
        if (!append_separator(&ctx->buffer, &first)) return 0;
        if (!tsmp_buffer_append(&ctx->buffer, "start_byte,end_byte")) return 0;
    }

    if (!append_header_field(ctx, &first, TSMP_FIELD_CHILD_COUNT, "child_count")) return 0;
    if (tsmp_has_field(ctx, TSMP_FIELD_DIAGNOSTICS)) {
        if (!append_separator(&ctx->buffer, &first)) return 0;
        if (!tsmp_buffer_append(&ctx->buffer, "is_error,is_missing,has_error")) return 0;
    }
    if (!append_header_field(ctx, &first, TSMP_FIELD_CHILDREN, "children")) return 0;
    return tsmp_buffer_append(&ctx->buffer, "\n");
}

static int append_children_csv_field(TsmpBuffer *buffer, const TsmpRenderCtx *ctx, TSNode node)
{
    TsmpBuffer children;
    if (!tsmp_buffer_init(&children, 256)) return 0;

    if (!tsmp_json_children(&children, ctx, node)) {
        tsmp_buffer_free(&children);
        return 0;
    }

    int ok = tsmp_buffer_append_csv_bytes(buffer, (const unsigned char *)children.data, children.len);
    tsmp_buffer_free(&children);
    return ok;
}

int tsmp_csv_node(TsmpRenderCtx *ctx, TSNode node, size_t node_id, size_t parent_id)
{
    TsmpBuffer *buffer = &ctx->buffer;
    TSPoint start_point = ts_node_start_point(node);
    TSPoint end_point = ts_node_end_point(node);
    int first = 1;

    if (tsmp_has_field(ctx, TSMP_FIELD_ID)) {
        if (!append_separator(buffer, &first)) return 0;
        if (!tsmp_buffer_append_size(buffer, node_id)) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_PARENT_ID)) {
        if (!append_separator(buffer, &first)) return 0;
        if (parent_id != 0 && !tsmp_buffer_append_size(buffer, parent_id)) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_RULE)) {
        const char *rule = ts_node_type(node);
        if (!append_separator(buffer, &first)) return 0;
        if (!tsmp_buffer_append_csv_bytes(buffer, (const unsigned char *)rule, strlen(rule))) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_TEXT)) {
        if (!append_separator(buffer, &first)) return 0;
        if (!tsmp_append_source_slice_csv(buffer, ctx, node)) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_RANGE)) {
        if (!append_separator(buffer, &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, start_point.row + 1)) return 0;
        if (!tsmp_buffer_append(buffer, ",")) return 0;
        if (!tsmp_buffer_append_u32(buffer, start_point.column)) return 0;
        if (!tsmp_buffer_append(buffer, ",")) return 0;
        if (!tsmp_buffer_append_u32(buffer, end_point.row + 1)) return 0;
        if (!tsmp_buffer_append(buffer, ",")) return 0;
        if (!tsmp_buffer_append_u32(buffer, end_point.column)) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_BYTE_RANGE)) {
        if (!append_separator(buffer, &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, ts_node_start_byte(node))) return 0;
        if (!tsmp_buffer_append(buffer, ",")) return 0;
        if (!tsmp_buffer_append_u32(buffer, ts_node_end_byte(node))) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_CHILD_COUNT)) {
        if (!append_separator(buffer, &first)) return 0;
        if (!tsmp_buffer_append_u32(buffer, ts_node_child_count(node))) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_DIAGNOSTICS)) {
        if (!append_separator(buffer, &first)) return 0;
        if (!tsmp_buffer_append(buffer, ts_node_is_error(node) ? "1" : "0")) return 0;
        if (!tsmp_buffer_append(buffer, ",")) return 0;
        if (!tsmp_buffer_append(buffer, ts_node_is_missing(node) ? "1" : "0")) return 0;
        if (!tsmp_buffer_append(buffer, ",")) return 0;
        if (!tsmp_buffer_append(buffer, ts_node_has_error(node) ? "1" : "0")) return 0;
    }
    if (tsmp_has_field(ctx, TSMP_FIELD_CHILDREN)) {
        if (!append_separator(buffer, &first)) return 0;
        if (!append_children_csv_field(buffer, ctx, node)) return 0;
    }

    return tsmp_buffer_append(buffer, "\n");
}
