#include "tsmp_languages.h"

#include <string.h>

typedef const TSLanguage *(*TsmpLanguageFn)(void);

typedef struct {
    const char *name;
    TsmpLanguageFn language;
} TsmpLanguageEntry;

extern const TSLanguage *tree_sitter_java(void);

static const TsmpLanguageEntry TSMP_LANGUAGES[] = {
    { "java", tree_sitter_java },
    { NULL, NULL }
};

const TSLanguage *tsmp_find_language(const char *name)
{
    if (!name) return NULL;

    for (int i = 0; TSMP_LANGUAGES[i].name != NULL; i++) {
        if (strcmp(TSMP_LANGUAGES[i].name, name) == 0) {
            return TSMP_LANGUAGES[i].language();
        }
    }

    return NULL;
}
