#include "tsmp_render.h"

#include <string.h>

int tsmp_has_field(const TsmpRenderCtx *ctx, unsigned int field)
{
    return (ctx->fields & field) != 0;
}

int tsmp_rule_filter_matches(const char *filter, const char *rule)
{
    if (!filter || !*filter) return 1;
    if (!rule || !*rule) return 0;

    size_t rule_len = strlen(rule);
    const char *start = filter;
    while (*start) {
        const char *end = strchr(start, '|');
        size_t len = end ? (size_t)(end - start) : strlen(start);

        while (len > 0 && *start == ' ') {
            start++;
            len--;
        }
        while (len > 0 && start[len - 1] == ' ') {
            len--;
        }

        if (len == rule_len && strncmp(start, rule, len) == 0) return 1;
        if (!end) break;
        start = end + 1;
    }

    return 0;
}

static void collect_diagnostics_walk(TSNode node, TsmpDiagnostics *diagnostics)
{
    if (ts_node_is_named(node)) {
        diagnostics->named_node_count++;
    }
    if (ts_node_has_error(node)) {
        diagnostics->has_errors = 1;
    }
    if (ts_node_is_error(node)) {
        uint32_t start = ts_node_start_byte(node);
        uint32_t end = ts_node_end_byte(node);
        diagnostics->error_node_count++;
        diagnostics->error_byte_count += end >= start ? (size_t)(end - start) : 0;
    }
    if (ts_node_is_missing(node)) {
        diagnostics->missing_node_count++;
    }

    uint32_t child_count = ts_node_child_count(node);
    for (uint32_t i = 0; i < child_count; i++) {
        collect_diagnostics_walk(ts_node_child(node, i), diagnostics);
    }
}

TsmpDiagnostics tsmp_collect_diagnostics(TSNode node)
{
    TsmpDiagnostics diagnostics;
    memset(&diagnostics, 0, sizeof(diagnostics));
    collect_diagnostics_walk(node, &diagnostics);
    return diagnostics;
}

int tsmp_render_diagnostics(
    const char *language,
    TsmpDiagnostics diagnostics,
    TsmpResult *out_result)
{
    TsmpBuffer buffer;
    if (!tsmp_buffer_init(&buffer, 256)) {
        out_result->status = TSMP_ERROR_OUT_OF_MEMORY;
        return TSMP_ERROR_OUT_OF_MEMORY;
    }

    if (!tsmp_buffer_append(&buffer, "{\"language\":")) goto oom;
    if (!tsmp_buffer_append_json_string(&buffer, language)) goto oom;
    if (!tsmp_buffer_append(&buffer, ",\"nodeCount\":")) goto oom;
    if (!tsmp_buffer_append_size(&buffer, diagnostics.named_node_count)) goto oom;
    if (!tsmp_buffer_append(&buffer, ",\"hasErrors\":")) goto oom;
    if (!tsmp_buffer_append(&buffer, diagnostics.has_errors ? "true" : "false")) goto oom;
    if (!tsmp_buffer_append(&buffer, ",\"errorNodeCount\":")) goto oom;
    if (!tsmp_buffer_append_size(&buffer, diagnostics.error_node_count)) goto oom;
    if (!tsmp_buffer_append(&buffer, ",\"missingNodeCount\":")) goto oom;
    if (!tsmp_buffer_append_size(&buffer, diagnostics.missing_node_count)) goto oom;
    if (!tsmp_buffer_append(&buffer, ",\"errorByteCount\":")) goto oom;
    if (!tsmp_buffer_append_size(&buffer, diagnostics.error_byte_count)) goto oom;
    if (!tsmp_buffer_append(&buffer, "}")) goto oom;

    size_t output_len = buffer.len;
    out_result->status = TSMP_OK;
    out_result->data = (unsigned char *)tsmp_buffer_take(&buffer);
    out_result->length = output_len;
    out_result->node_count = diagnostics.named_node_count;
    out_result->error_message = NULL;
    return TSMP_OK;

oom:
    tsmp_buffer_free(&buffer);
    out_result->status = TSMP_ERROR_OUT_OF_MEMORY;
    return TSMP_ERROR_OUT_OF_MEMORY;
}

int tsmp_append_source_slice_json(TsmpBuffer *buffer, const TsmpRenderCtx *ctx, TSNode node)
{
    uint32_t start = ts_node_start_byte(node);
    uint32_t end = ts_node_end_byte(node);
    if (end < start) end = start;
    if ((size_t)start > ctx->source_len) start = (uint32_t)ctx->source_len;
    if ((size_t)end > ctx->source_len) end = (uint32_t)ctx->source_len;
    return tsmp_buffer_append_json_bytes(buffer, ctx->source + start, (size_t)(end - start));
}

int tsmp_append_source_slice_csv(TsmpBuffer *buffer, const TsmpRenderCtx *ctx, TSNode node)
{
    uint32_t start = ts_node_start_byte(node);
    uint32_t end = ts_node_end_byte(node);
    if (end < start) end = start;
    if ((size_t)start > ctx->source_len) start = (uint32_t)ctx->source_len;
    if ((size_t)end > ctx->source_len) end = (uint32_t)ctx->source_len;
    return tsmp_buffer_append_csv_bytes(buffer, ctx->source + start, (size_t)(end - start));
}

static size_t count_walk(const TsmpOptions *options, TSNode node)
{
    size_t count = 0;

    if (ts_node_is_named(node) && tsmp_rule_filter_matches(options->include_rules, ts_node_type(node))) {
        count++;
    }

    uint32_t child_count = ts_node_child_count(node);
    for (uint32_t i = 0; i < child_count; i++) {
        count += count_walk(options, ts_node_child(node, i));
    }

    return count;
}

static int render_walk(TsmpRenderCtx *ctx, TSNode node, size_t parent_id)
{
    if (!ts_node_is_named(node)) return 1;

    const char *rule = ts_node_type(node);
    int included = tsmp_rule_filter_matches(ctx->options->include_rules, rule);
    size_t current_id = parent_id;

    if (included) {
        current_id = ctx->next_id++;
        if (ctx->options->format == TSMP_FORMAT_JSON) {
            if (!tsmp_json_node(ctx, node, current_id, parent_id)) return 0;
        } else if (ctx->options->format == TSMP_FORMAT_CSV) {
            if (!tsmp_csv_node(ctx, node, current_id, parent_id)) return 0;
        } else if (ctx->options->format == TSMP_FORMAT_BINARY) {
            if (!tsmp_binary_node(ctx, node, current_id, parent_id)) return 0;
        } else {
            return 0;
        }
        ctx->node_count++;
    }

    uint32_t child_count = ts_node_child_count(node);
    for (uint32_t i = 0; i < child_count; i++) {
        if (!render_walk(ctx, ts_node_child(node, i), current_id)) return 0;
    }

    return 1;
}

int tsmp_render_tree(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptions *options,
    TSTree *tree,
    TsmpResult *out_result)
{
    TsmpRenderCtx ctx;
    memset(&ctx, 0, sizeof(ctx));
    ctx.source = source;
    ctx.source_len = source_len;
    ctx.options = options;
    ctx.fields = options->fields == 0 ? TSMP_FIELD_ALL : options->fields;
    ctx.next_id = 1;

    int needs_diagnostics =
        options->format == TSMP_FORMAT_DIAGNOSTICS ||
        ((options->format == TSMP_FORMAT_JSON || options->format == TSMP_FORMAT_BINARY) &&
         tsmp_has_field(&ctx, TSMP_FIELD_DIAGNOSTICS));
    if (needs_diagnostics) {
        ctx.diagnostics = tsmp_collect_diagnostics(ts_tree_root_node(tree));
    }

    if (options->format == TSMP_FORMAT_DIAGNOSTICS) {
        return tsmp_render_diagnostics(options->language, ctx.diagnostics, out_result);
    }

    size_t total_nodes = 0;
    if (options->format == TSMP_FORMAT_STATS || options->format == TSMP_FORMAT_BINARY) {
        total_nodes = count_walk(options, ts_tree_root_node(tree));
    }

    if (options->format == TSMP_FORMAT_STATS) {
        out_result->status = TSMP_OK;
        out_result->data = NULL;
        out_result->length = 0;
        out_result->node_count = total_nodes;
        out_result->error_message = NULL;
        return TSMP_OK;
    }

    if (!tsmp_buffer_init(&ctx.buffer, 4096)) {
        out_result->status = TSMP_ERROR_OUT_OF_MEMORY;
        return TSMP_ERROR_OUT_OF_MEMORY;
    }

    if (options->format == TSMP_FORMAT_JSON) {
        if (!tsmp_json_begin(&ctx)) goto oom;
    } else if (options->format == TSMP_FORMAT_CSV) {
        if (!tsmp_csv_begin(&ctx)) goto oom;
    } else if (options->format == TSMP_FORMAT_BINARY) {
        if (!tsmp_binary_begin(&ctx, total_nodes)) goto oom;
    } else {
        tsmp_buffer_free(&ctx.buffer);
        return TSMP_ERROR_UNSUPPORTED_FORMAT;
    }

    if (!render_walk(&ctx, ts_tree_root_node(tree), 0)) goto oom;

    if (options->format == TSMP_FORMAT_JSON && !tsmp_json_end(&ctx)) goto oom;
    if (options->format == TSMP_FORMAT_BINARY && !tsmp_binary_end(&ctx, total_nodes)) goto oom;

    size_t output_len = ctx.buffer.len;
    out_result->status = TSMP_OK;
    out_result->data = (unsigned char *)tsmp_buffer_take(&ctx.buffer);
    out_result->length = output_len;
    out_result->node_count = ctx.node_count;
    out_result->error_message = NULL;
    return TSMP_OK;

oom:
    tsmp_buffer_free(&ctx.buffer);
    out_result->status = TSMP_ERROR_OUT_OF_MEMORY;
    return TSMP_ERROR_OUT_OF_MEMORY;
}
