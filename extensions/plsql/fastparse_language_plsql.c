#include "../../include/tsmp.h"

#ifdef _WIN32
#define FASTPARSE_EXTENSION_API __declspec(dllexport)
#else
#define FASTPARSE_EXTENSION_API __attribute__((visibility("default")))
#endif

extern const TSLanguage *tree_sitter_plsql(void);

static const FastParseLanguageDescriptor FASTPARSE_PLSQL_LANGUAGE = {
    1u,
    "plsql",
    "Oracle PL/SQL",
    "tree_sitter_plsql",
    tree_sitter_plsql
};

FASTPARSE_EXTENSION_API const FastParseLanguageDescriptor *fastparse_language_extension_descriptor(void)
{
    return &FASTPARSE_PLSQL_LANGUAGE;
}
