#ifndef TSMP_BUFFER_H
#define TSMP_BUFFER_H

#include <stddef.h>
#include <stdint.h>

typedef struct {
    char *data;
    size_t len;
    size_t cap;
} TsmpBuffer;

int tsmp_buffer_init(TsmpBuffer *buffer, size_t initial_capacity);
void tsmp_buffer_free(TsmpBuffer *buffer);
char *tsmp_buffer_take(TsmpBuffer *buffer);

int tsmp_buffer_reserve(TsmpBuffer *buffer, size_t extra);
int tsmp_buffer_append(TsmpBuffer *buffer, const char *text);
int tsmp_buffer_append_bytes(TsmpBuffer *buffer, const unsigned char *data, size_t len);
int tsmp_buffer_append_size(TsmpBuffer *buffer, size_t value);
int tsmp_buffer_append_u32(TsmpBuffer *buffer, uint32_t value);
int tsmp_buffer_append_json_string(TsmpBuffer *buffer, const char *text);
int tsmp_buffer_append_json_bytes(TsmpBuffer *buffer, const unsigned char *data, size_t len);
int tsmp_buffer_append_csv_bytes(TsmpBuffer *buffer, const unsigned char *data, size_t len);

#endif /* TSMP_BUFFER_H */
