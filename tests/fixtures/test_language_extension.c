#include "../../include/tsmp.h"

#ifdef _WIN32
#define FASTPARSE_EXTENSION_API __declspec(dllexport)
#else
#define FASTPARSE_EXTENSION_API __attribute__((visibility("default")))
#endif

extern const TSLanguage *tree_sitter_java(void);

static const FastParseLanguageDescriptor FASTPARSE_TEST_LANGUAGE = {
    1u,
    "java_extension",
    "Java Test Extension",
    "tree_sitter_java",
    tree_sitter_java
};

FASTPARSE_EXTENSION_API const FastParseLanguageDescriptor *fastparse_language_extension_descriptor(void)
{
    return &FASTPARSE_TEST_LANGUAGE;
}
