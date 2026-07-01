#include "../../include/tsmp.h"

#ifdef _WIN32
#define FASTPARSE_EXTENSION_API __declspec(dllexport)
#else
#define FASTPARSE_EXTENSION_API __attribute__((visibility("default")))
#endif

extern const TSLanguage *tree_sitter_javaswing(void);

static const FastParseLanguageDescriptor FASTPARSE_JAVASWING_LANGUAGE = {
    1u,
    "javaswing",
    "Java Swing",
    "tree_sitter_javaswing",
    tree_sitter_javaswing
};

FASTPARSE_EXTENSION_API const FastParseLanguageDescriptor *fastparse_language_extension_descriptor(void)
{
    return &FASTPARSE_JAVASWING_LANGUAGE;
}
