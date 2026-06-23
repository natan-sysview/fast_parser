#include "tsmp_languages.h"

#include <stdlib.h>
#include <string.h>

#define TSMP_LANGUAGE_EXTENSION_ABI_VERSION 1u
#define TSMP_MAX_EXTENSION_LANGUAGES 64u

typedef struct {
    const char *name;
    FastParseLanguageFn language;
} TsmpLanguageEntry;

typedef struct {
    char *name;
    char *display_name;
    FastParseLanguageFn language;
    void *library_handle;
} TsmpExtensionLanguage;

extern const TSLanguage *tree_sitter_java(void);

static const TsmpLanguageEntry TSMP_LANGUAGES[] = {
    { "java", tree_sitter_java },
    { NULL, NULL }
};

static TsmpExtensionLanguage TSMP_EXTENSION_LANGUAGES[TSMP_MAX_EXTENSION_LANGUAGES];
static size_t TSMP_EXTENSION_LANGUAGE_COUNT = 0;

static char *copy_text(const char *value)
{
    const char *safe = value ? value : "";
    size_t len = strlen(safe);
    char *copy = malloc(len + 1);
    if (!copy) return NULL;
    memcpy(copy, safe, len + 1);
    return copy;
}

static void load_result_init(FastParseLanguageLoadResult *result)
{
    if (!result) return;
    result->status = TSMP_OK;
    result->language = NULL;
    result->display_name = NULL;
    result->error_message = NULL;
}

static int load_result_set_error(
    FastParseLanguageLoadResult *result,
    int status,
    const char *message)
{
    if (!result) return status;
    result->status = status;
    result->language = NULL;
    result->display_name = NULL;
    result->error_message = copy_text(message);
    if (!result->error_message && message) {
        result->status = TSMP_ERROR_OUT_OF_MEMORY;
    }
    return result->status;
}

static int load_result_set_success(
    FastParseLanguageLoadResult *result,
    const char *language,
    const char *display_name)
{
    if (!result) return TSMP_OK;
    result->status = TSMP_OK;
    result->language = copy_text(language);
    result->display_name = copy_text(display_name ? display_name : language);
    result->error_message = NULL;
    if (!result->language || !result->display_name) {
        free(result->language);
        free(result->display_name);
        result->language = NULL;
        result->display_name = NULL;
        result->status = TSMP_ERROR_OUT_OF_MEMORY;
    }
    return result->status;
}

const TSLanguage *tsmp_find_language(const char *name)
{
    if (!name) return NULL;

    for (int i = 0; TSMP_LANGUAGES[i].name != NULL; i++) {
        if (strcmp(TSMP_LANGUAGES[i].name, name) == 0) {
            return TSMP_LANGUAGES[i].language();
        }
    }

    for (size_t i = 0; i < TSMP_EXTENSION_LANGUAGE_COUNT; i++) {
        if (strcmp(TSMP_EXTENSION_LANGUAGES[i].name, name) == 0) {
            return TSMP_EXTENSION_LANGUAGES[i].language();
        }
    }

    return NULL;
}

int tsmp_language_available(const char *name)
{
    return tsmp_find_language(name) != NULL;
}

int tsmp_register_language_extension(
    const FastParseLanguageDescriptor *descriptor,
    void *library_handle,
    FastParseLanguageLoadResult *out_result)
{
    load_result_init(out_result);

    if (!descriptor) {
        return load_result_set_error(out_result, TSMP_ERROR_EXTENSION_LOAD, "Language extension descriptor is missing.");
    }
    if (descriptor->abi_version != TSMP_LANGUAGE_EXTENSION_ABI_VERSION) {
        return load_result_set_error(out_result, TSMP_ERROR_EXTENSION_LOAD, "Language extension ABI version is not supported.");
    }
    if (!descriptor->language || !*descriptor->language || !descriptor->language_fn) {
        return load_result_set_error(out_result, TSMP_ERROR_EXTENSION_LOAD, "Language extension descriptor is incomplete.");
    }
    if (tsmp_find_language(descriptor->language)) {
        return load_result_set_error(out_result, TSMP_ERROR_EXTENSION_LOAD, "Language is already registered.");
    }
    if (TSMP_EXTENSION_LANGUAGE_COUNT >= TSMP_MAX_EXTENSION_LANGUAGES) {
        return load_result_set_error(out_result, TSMP_ERROR_EXTENSION_LOAD, "Language extension registry is full.");
    }
    if (!descriptor->language_fn()) {
        return load_result_set_error(out_result, TSMP_ERROR_EXTENSION_LOAD, "Language extension returned a null Tree-sitter language.");
    }

    TsmpExtensionLanguage *entry = &TSMP_EXTENSION_LANGUAGES[TSMP_EXTENSION_LANGUAGE_COUNT];
    entry->name = copy_text(descriptor->language);
    entry->display_name = copy_text(descriptor->display_name ? descriptor->display_name : descriptor->language);
    entry->language = descriptor->language_fn;
    entry->library_handle = library_handle;
    if (!entry->name || !entry->display_name) {
        free(entry->name);
        free(entry->display_name);
        memset(entry, 0, sizeof(*entry));
        return load_result_set_error(out_result, TSMP_ERROR_OUT_OF_MEMORY, "Could not register language extension.");
    }

    TSMP_EXTENSION_LANGUAGE_COUNT++;
    return load_result_set_success(out_result, entry->name, entry->display_name);
}
