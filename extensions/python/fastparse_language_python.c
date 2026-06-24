#include "../../include/tsmp.h"

#ifdef _WIN32
#define FASTPARSE_EXTENSION_API __declspec(dllexport)
#else
#define FASTPARSE_EXTENSION_API __attribute__((visibility("default")))
#endif

extern const TSLanguage *tree_sitter_python(void);

static const FastParseLanguageDescriptor FASTPARSE_PYTHON_LANGUAGE = {
    1u,
    "python",
    "Python",
    "tree_sitter_python",
    tree_sitter_python
};

FASTPARSE_EXTENSION_API const FastParseLanguageDescriptor *fastparse_language_extension_descriptor(void)
{
    return &FASTPARSE_PYTHON_LANGUAGE;
}
