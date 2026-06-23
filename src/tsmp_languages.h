#ifndef TSMP_LANGUAGES_H
#define TSMP_LANGUAGES_H

#include "../include/tsmp.h"

#include <tree_sitter/api.h>

const TSLanguage *tsmp_find_language(const char *name);
int tsmp_language_available(const char *name);
int tsmp_register_language_extension(
    const FastParseLanguageDescriptor *descriptor,
    void *library_handle,
    FastParseLanguageLoadResult *out_result);

#endif /* TSMP_LANGUAGES_H */
