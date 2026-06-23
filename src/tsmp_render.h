#ifndef TSMP_RENDER_H
#define TSMP_RENDER_H

#include "../include/tsmp.h"
#include "tsmp_buffer.h"

#include <tree_sitter/api.h>

typedef struct {
    int has_errors;
    size_t error_node_count;
    size_t missing_node_count;
    size_t error_byte_count;
} TsmpDiagnostics;

typedef struct {
    const unsigned char *source;
    size_t source_len;
    const TsmpOptions *options;
    unsigned int fields;
    TsmpDiagnostics diagnostics;
    TsmpBuffer buffer;
    size_t node_count;
    size_t next_id;
} TsmpRenderCtx;

int tsmp_has_field(const TsmpRenderCtx *ctx, unsigned int field);
int tsmp_rule_filter_matches(const char *filter, const char *rule);
TsmpDiagnostics tsmp_collect_diagnostics(TSNode node);

int tsmp_append_source_slice_json(TsmpBuffer *buffer, const TsmpRenderCtx *ctx, TSNode node);
int tsmp_append_source_slice_csv(TsmpBuffer *buffer, const TsmpRenderCtx *ctx, TSNode node);

int tsmp_render_tree(
    const unsigned char *source,
    size_t source_len,
    const TsmpOptions *options,
    TSTree *tree,
    TsmpResult *out_result);

int tsmp_json_begin(TsmpRenderCtx *ctx);
int tsmp_json_node(TsmpRenderCtx *ctx, TSNode node, size_t node_id, size_t parent_id);
int tsmp_json_end(TsmpRenderCtx *ctx);
int tsmp_json_children(TsmpBuffer *buffer, const TsmpRenderCtx *ctx, TSNode node);

int tsmp_csv_begin(TsmpRenderCtx *ctx);
int tsmp_csv_node(TsmpRenderCtx *ctx, TSNode node, size_t node_id, size_t parent_id);

int tsmp_binary_begin(TsmpRenderCtx *ctx, size_t total_nodes);
int tsmp_binary_node(TsmpRenderCtx *ctx, TSNode node, size_t node_id, size_t parent_id);
int tsmp_binary_end(TsmpRenderCtx *ctx, size_t total_nodes);

#endif /* TSMP_RENDER_H */
