#include "tsmp_buffer.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int tsmp_buffer_init(TsmpBuffer *buffer, size_t initial_capacity)
{
    if (!buffer) return 0;
    if (initial_capacity == 0) initial_capacity = 4096;
    buffer->data = malloc(initial_capacity);
    if (!buffer->data) return 0;
    buffer->len = 0;
    buffer->cap = initial_capacity;
    buffer->data[0] = '\0';
    return 1;
}

void tsmp_buffer_free(TsmpBuffer *buffer)
{
    if (!buffer) return;
    free(buffer->data);
    buffer->data = NULL;
    buffer->len = 0;
    buffer->cap = 0;
}

char *tsmp_buffer_take(TsmpBuffer *buffer)
{
    if (!buffer) return NULL;
    char *data = buffer->data;
    buffer->data = NULL;
    buffer->len = 0;
    buffer->cap = 0;
    return data;
}

int tsmp_buffer_reserve(TsmpBuffer *buffer, size_t extra)
{
    if (!buffer || !buffer->data) return 0;

    size_t required = buffer->len + extra + 1;
    if (required <= buffer->cap) return 1;

    size_t next = buffer->cap;
    while (next < required) {
        next *= 2;
    }

    char *grown = realloc(buffer->data, next);
    if (!grown) return 0;

    buffer->data = grown;
    buffer->cap = next;
    return 1;
}

int tsmp_buffer_append(TsmpBuffer *buffer, const char *text)
{
    if (!text) text = "";
    return tsmp_buffer_append_bytes(buffer, (const unsigned char *)text, strlen(text));
}

int tsmp_buffer_append_bytes(TsmpBuffer *buffer, const unsigned char *data, size_t len)
{
    if (!tsmp_buffer_reserve(buffer, len)) return 0;
    if (len > 0 && data) {
        memcpy(buffer->data + buffer->len, data, len);
    }
    buffer->len += len;
    buffer->data[buffer->len] = '\0';
    return 1;
}

int tsmp_buffer_append_size(TsmpBuffer *buffer, size_t value)
{
    char temp[64];
    snprintf(temp, sizeof(temp), "%zu", value);
    return tsmp_buffer_append(buffer, temp);
}

int tsmp_buffer_append_u32(TsmpBuffer *buffer, uint32_t value)
{
    char temp[64];
    snprintf(temp, sizeof(temp), "%u", value);
    return tsmp_buffer_append(buffer, temp);
}

int tsmp_buffer_append_json_string(TsmpBuffer *buffer, const char *text)
{
    return tsmp_buffer_append_json_bytes(
        buffer,
        (const unsigned char *)(text ? text : ""),
        text ? strlen(text) : 0);
}

int tsmp_buffer_append_json_bytes(TsmpBuffer *buffer, const unsigned char *data, size_t len)
{
    if (!tsmp_buffer_append(buffer, "\"")) return 0;

    for (size_t i = 0; i < len; i++) {
        unsigned char c = data[i];
        char escaped[8];
        switch (c) {
            case '"':
                if (!tsmp_buffer_append(buffer, "\\\"")) return 0;
                break;
            case '\\':
                if (!tsmp_buffer_append(buffer, "\\\\")) return 0;
                break;
            case '\n':
                if (!tsmp_buffer_append(buffer, "\\n")) return 0;
                break;
            case '\r':
                if (!tsmp_buffer_append(buffer, "\\r")) return 0;
                break;
            case '\t':
                if (!tsmp_buffer_append(buffer, "\\t")) return 0;
                break;
            default:
                if (c < 0x20 || c >= 0x80) {
                    snprintf(escaped, sizeof(escaped), "\\u%04x", c);
                    if (!tsmp_buffer_append(buffer, escaped)) return 0;
                } else if (!tsmp_buffer_append_bytes(buffer, &c, 1)) {
                    return 0;
                }
                break;
        }
    }

    return tsmp_buffer_append(buffer, "\"");
}

int tsmp_buffer_append_csv_bytes(TsmpBuffer *buffer, const unsigned char *data, size_t len)
{
    if (!tsmp_buffer_append(buffer, "\"")) return 0;

    for (size_t i = 0; i < len; i++) {
        unsigned char c = data[i];
        if (c == '"') {
            if (!tsmp_buffer_append(buffer, "\"\"")) return 0;
        } else if (c == '\0') {
            if (!tsmp_buffer_append(buffer, "\\0")) return 0;
        } else if (!tsmp_buffer_append_bytes(buffer, &c, 1)) {
            return 0;
        }
    }

    return tsmp_buffer_append(buffer, "\"");
}
