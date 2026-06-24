#include "../../include/tsmp.h"

#ifdef _WIN32
#define FASTPARSE_EXTENSION_API __declspec(dllexport)
#else
#define FASTPARSE_EXTENSION_API __attribute__((visibility("default")))
#endif

extern const TSLanguage *tree_sitter_rust(void);

static const FastParseLanguageDescriptor FASTPARSE_RUST_LANGUAGE = {
    1u,
    "rust",
    "Rust",
    "tree_sitter_rust",
    tree_sitter_rust
};

FASTPARSE_EXTENSION_API const FastParseLanguageDescriptor *fastparse_language_extension_descriptor(void)
{
    return &FASTPARSE_RUST_LANGUAGE;
}
