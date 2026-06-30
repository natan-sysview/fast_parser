#include "../../include/tsmp.h"

#ifdef _WIN32
#define FASTPARSE_EXTENSION_API __declspec(dllexport)
#else
#define FASTPARSE_EXTENSION_API __attribute__((visibility("default")))
#endif

extern const TSLanguage *tree_sitter_java_frameworks(void);

static const FastParseLanguageDescriptor FASTPARSE_JAVA_FRAMEWORKS_LANGUAGE = {
    1u,
    "java-frameworks",
    "Java Frameworks Experimental",
    "tree_sitter_java_frameworks",
    tree_sitter_java_frameworks
};

FASTPARSE_EXTENSION_API const FastParseLanguageDescriptor *fastparse_language_extension_descriptor(void)
{
    return &FASTPARSE_JAVA_FRAMEWORKS_LANGUAGE;
}
