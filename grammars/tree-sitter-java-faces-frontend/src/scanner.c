#include "tree_sitter/parser.h"
#include "tree_sitter/array.h"

#include <ctype.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <wctype.h>

enum TokenType {
    PI_TARGET,
    PI_CONTENT,
    COMMENT,
    CHAR_DATA,
    CDATA,
    XML_MODEL,
    XML_STYLESHEET,
    GENERIC_START_TAG_NAME,
    FACELETS_START_TAG_NAME,
    JSF_HTML_START_TAG_NAME,
    JSF_CORE_START_TAG_NAME,
    COMPOSITE_START_TAG_NAME,
    FACES_START_TAG_NAME,
    PRIMEFACES_START_TAG_NAME,
    PRIMEFACES_EXTENSIONS_START_TAG_NAME,
    JSTL_START_TAG_NAME,
    QUALIFIED_START_TAG_NAME,
    GENERIC_END_TAG_NAME,
    FACELETS_END_TAG_NAME,
    JSF_HTML_END_TAG_NAME,
    JSF_CORE_END_TAG_NAME,
    COMPOSITE_END_TAG_NAME,
    FACES_END_TAG_NAME,
    PRIMEFACES_END_TAG_NAME,
    PRIMEFACES_EXTENSIONS_END_TAG_NAME,
    JSTL_END_TAG_NAME,
    QUALIFIED_END_TAG_NAME,
    EL_QUALIFIED_FUNCTION_NAME,
    ERRONEOUS_END_NAME,
    SELF_CLOSING_TAG_DELIMITER,
};

typedef Array(char) String;
typedef Array(String) Vector;

static inline void advance(TSLexer *lexer) {
    lexer->advance(lexer, false);
}

static inline bool advance_if(TSLexer *lexer, wchar_t character) {
    if (lexer->eof(lexer) || lexer->lookahead != character) {
        return false;
    }
    advance(lexer);
    return true;
}

static inline bool is_valid_name_char(wchar_t character) {
    return iswalnum(character) || character == '_' || character == ':' ||
           character == '.' || character == '-' || character == 0xB7;
}

static inline bool is_valid_name_start_char(wchar_t character) {
    return iswalpha(character) || character == '_' || character == ':';
}

static inline bool string_eq(const String *left, const String *right) {
    return left->size == right->size &&
           memcmp(left->contents, right->contents, left->size) == 0;
}

static inline bool has_prefix(const String *name, const char *prefix) {
    const size_t length = strlen(prefix);
    return name->size > length && name->contents[length] == ':' &&
           memcmp(name->contents, prefix, length) == 0;
}

static inline bool is_qualified(const String *name) {
    for (uint32_t index = 0; index < name->size; ++index) {
        if (name->contents[index] == ':') {
            return true;
        }
    }
    return false;
}

static enum TokenType start_symbol_for(const String *name) {
    if (has_prefix(name, "ui")) return FACELETS_START_TAG_NAME;
    if (has_prefix(name, "h")) return JSF_HTML_START_TAG_NAME;
    if (has_prefix(name, "f")) return JSF_CORE_START_TAG_NAME;
    if (has_prefix(name, "cc")) return COMPOSITE_START_TAG_NAME;
    if (has_prefix(name, "faces") || has_prefix(name, "jsf")) return FACES_START_TAG_NAME;
    if (has_prefix(name, "p")) return PRIMEFACES_START_TAG_NAME;
    if (has_prefix(name, "pe") || has_prefix(name, "poue")) {
        return PRIMEFACES_EXTENSIONS_START_TAG_NAME;
    }
    if (has_prefix(name, "c")) return JSTL_START_TAG_NAME;
    if (is_qualified(name)) return QUALIFIED_START_TAG_NAME;
    return GENERIC_START_TAG_NAME;
}

static enum TokenType end_symbol_for(const String *name) {
    switch (start_symbol_for(name)) {
        case FACELETS_START_TAG_NAME: return FACELETS_END_TAG_NAME;
        case JSF_HTML_START_TAG_NAME: return JSF_HTML_END_TAG_NAME;
        case JSF_CORE_START_TAG_NAME: return JSF_CORE_END_TAG_NAME;
        case COMPOSITE_START_TAG_NAME: return COMPOSITE_END_TAG_NAME;
        case FACES_START_TAG_NAME: return FACES_END_TAG_NAME;
        case PRIMEFACES_START_TAG_NAME: return PRIMEFACES_END_TAG_NAME;
        case PRIMEFACES_EXTENSIONS_START_TAG_NAME: return PRIMEFACES_EXTENSIONS_END_TAG_NAME;
        case JSTL_START_TAG_NAME: return JSTL_END_TAG_NAME;
        case QUALIFIED_START_TAG_NAME: return QUALIFIED_END_TAG_NAME;
        default: return GENERIC_END_TAG_NAME;
    }
}

static String scan_tag_name(TSLexer *lexer) {
    String tag_name = array_new();
    if (is_valid_name_start_char(lexer->lookahead)) {
        array_push(&tag_name, (char)lexer->lookahead);
        advance(lexer);
    }
    while (is_valid_name_char(lexer->lookahead)) {
        array_push(&tag_name, (char)lexer->lookahead);
        advance(lexer);
    }
    return tag_name;
}

static bool scan_start_tag_name(Vector *tags, TSLexer *lexer, const bool *valid_symbols) {
    String tag_name = scan_tag_name(lexer);
    if (tag_name.size == 0) {
        array_delete(&tag_name);
        return false;
    }

    const enum TokenType symbol = start_symbol_for(&tag_name);
    if (!valid_symbols[symbol]) {
        array_delete(&tag_name);
        return false;
    }

    lexer->result_symbol = symbol;
    array_push(tags, tag_name);
    return true;
}

static bool scan_end_tag_name(Vector *tags, TSLexer *lexer, const bool *valid_symbols) {
    String tag_name = scan_tag_name(lexer);
    if (tag_name.size == 0) {
        array_delete(&tag_name);
        return false;
    }

    if (tags->size > 0 && string_eq(array_back(tags), &tag_name)) {
        const enum TokenType symbol = end_symbol_for(&tag_name);
        if (valid_symbols[symbol]) {
            String last_tag = array_pop(tags);
            array_delete(&last_tag);
            lexer->result_symbol = symbol;
            array_delete(&tag_name);
            return true;
        }
    }

    if (valid_symbols[ERRONEOUS_END_NAME]) {
        lexer->result_symbol = ERRONEOUS_END_NAME;
        array_delete(&tag_name);
        return true;
    }

    array_delete(&tag_name);
    return false;
}

static bool scan_self_closing_tag_delimiter(Vector *tags, TSLexer *lexer) {
    advance(lexer);
    if (!advance_if(lexer, '>')) {
        return false;
    }
    if (tags->size > 0) {
        String last_tag = array_pop(tags);
        array_delete(&last_tag);
    }
    lexer->result_symbol = SELF_CLOSING_TAG_DELIMITER;
    return true;
}

static inline bool in_error_recovery(const bool *valid_symbols) {
    return valid_symbols[PI_TARGET] && valid_symbols[PI_CONTENT] &&
           valid_symbols[COMMENT] && valid_symbols[CHAR_DATA] &&
           valid_symbols[CDATA];
}

static inline bool in_char_data(TSLexer *lexer) {
    return !lexer->eof(lexer) && lexer->lookahead != '<' && lexer->lookahead != '&';
}

static bool scan_char_data(TSLexer *lexer) {
    bool advanced_once = false;

    while (in_char_data(lexer)) {
        if (lexer->lookahead == '\\') {
            advance(lexer);
            advanced_once = true;
            if (lexer->lookahead == '\\' || lexer->lookahead == '#' || lexer->lookahead == '$') {
                advance(lexer);
            }
            continue;
        }

        if (lexer->lookahead == '#' || lexer->lookahead == '$') {
            lexer->mark_end(lexer);
            advance(lexer);
            if (lexer->lookahead == '{') {
                if (advanced_once) {
                    lexer->result_symbol = CHAR_DATA;
                    return true;
                }
                return false;
            }
            advanced_once = true;
            continue;
        }

        if (lexer->lookahead == ']') {
            lexer->mark_end(lexer);
            advance(lexer);
            if (lexer->lookahead == ']') {
                advance(lexer);
                if (lexer->lookahead == '>') {
                    advance(lexer);
                    if (advanced_once) {
                        lexer->result_symbol = CHAR_DATA;
                        return false;
                    }
                }
            }
        } else {
            advance(lexer);
        }
        advanced_once = true;
    }

    if (advanced_once) {
        lexer->mark_end(lexer);
        lexer->result_symbol = CHAR_DATA;
        return true;
    }
    return false;
}

static bool scan_cdata(TSLexer *lexer) {
    bool advanced_once = false;
    while (!lexer->eof(lexer)) {
        if (lexer->lookahead == ']') {
            lexer->mark_end(lexer);
            advance(lexer);
            if (lexer->lookahead == ']') {
                advance(lexer);
                if (lexer->lookahead == '>' && advanced_once) {
                    lexer->result_symbol = CDATA;
                    return true;
                }
            }
        }
        advanced_once = true;
        advance(lexer);
    }
    return false;
}

static bool check_word(TSLexer *lexer, const char *word, unsigned length) {
    for (unsigned index = 0; index < length; ++index) {
        if (!advance_if(lexer, word[index])) return false;
    }
    return true;
}

static bool scan_pi_target(TSLexer *lexer, const bool *valid_symbols) {
    bool advanced_once = false;
    bool found_x_first = false;

    if (is_valid_name_start_char(lexer->lookahead)) {
        if (lexer->lookahead == 'x' || lexer->lookahead == 'X') {
            found_x_first = true;
            lexer->mark_end(lexer);
        }
        advanced_once = true;
        advance(lexer);
    }

    if (!advanced_once) return false;

    while (is_valid_name_char(lexer->lookahead)) {
        if (found_x_first && (lexer->lookahead == 'm' || lexer->lookahead == 'M')) {
            advance(lexer);
            if (lexer->lookahead == 'l' || lexer->lookahead == 'L') {
                advance(lexer);
                if (is_valid_name_char(lexer->lookahead)) {
                    found_x_first = false;
                    const bool hyphen = lexer->lookahead == '-';
                    advance(lexer);
                    if (hyphen) {
                        if (valid_symbols[XML_MODEL] && check_word(lexer, "model", 5)) return false;
                        if (valid_symbols[XML_STYLESHEET] && check_word(lexer, "stylesheet", 10)) return false;
                    }
                } else {
                    return false;
                }
            }
        }
        found_x_first = false;
        advance(lexer);
    }

    lexer->mark_end(lexer);
    lexer->result_symbol = PI_TARGET;
    return true;
}

static bool scan_pi_content(TSLexer *lexer) {
    while (!lexer->eof(lexer) && lexer->lookahead != '\n' && lexer->lookahead != '?') {
        advance(lexer);
    }
    if (lexer->lookahead != '?') return false;

    lexer->mark_end(lexer);
    advance(lexer);
    if (lexer->lookahead != '>') return false;

    advance(lexer);
    while (lexer->lookahead == ' ') advance(lexer);
    if (lexer->lookahead == '\n') advance(lexer);
    lexer->result_symbol = PI_CONTENT;
    return true;
}

static bool scan_comment(TSLexer *lexer) {
    if (!advance_if(lexer, '-') || !advance_if(lexer, '-')) return false;

    while (!lexer->eof(lexer)) {
        if (lexer->lookahead == '-') {
            advance(lexer);
            if (lexer->lookahead == '-') {
                advance(lexer);
                break;
            }
        } else {
            advance(lexer);
        }
    }

    if (!advance_if(lexer, '>')) return false;
    lexer->mark_end(lexer);
    lexer->result_symbol = COMMENT;
    return true;
}

static inline bool is_el_identifier_start(wchar_t character) {
    return iswalpha(character) || character == '_' || character == '$' || character == '#';
}

static inline bool is_el_identifier_part(wchar_t character) {
    return iswalnum(character) || character == '_' || character == '$';
}

static bool scan_el_qualified_function_name(TSLexer *lexer) {
    if (!is_el_identifier_start(lexer->lookahead)) return false;
    advance(lexer);
    while (is_el_identifier_part(lexer->lookahead)) advance(lexer);
    if (!advance_if(lexer, ':')) return false;
    if (!is_el_identifier_start(lexer->lookahead)) return false;
    advance(lexer);
    while (is_el_identifier_part(lexer->lookahead)) advance(lexer);

    lexer->mark_end(lexer);
    while (lexer->lookahead == ' ' || lexer->lookahead == '\t' ||
           lexer->lookahead == '\r' || lexer->lookahead == '\n') {
        advance(lexer);
    }
    if (lexer->lookahead != '(') return false;

    lexer->result_symbol = EL_QUALIFIED_FUNCTION_NAME;
    return true;
}

bool tree_sitter_java_faces_frontend_external_scanner_scan(
    void *payload,
    TSLexer *lexer,
    const bool *valid_symbols
) {
    Vector *tags = (Vector *)payload;

    if (in_error_recovery(valid_symbols)) return false;
    if (valid_symbols[PI_TARGET]) return scan_pi_target(lexer, valid_symbols);
    if (valid_symbols[PI_CONTENT]) return scan_pi_content(lexer);
    if (valid_symbols[CHAR_DATA] && scan_char_data(lexer)) return true;
    if (valid_symbols[CDATA] && scan_cdata(lexer)) return true;
    if (valid_symbols[EL_QUALIFIED_FUNCTION_NAME] && scan_el_qualified_function_name(lexer)) {
        return true;
    }

    switch (lexer->lookahead) {
        case '<':
            lexer->mark_end(lexer);
            advance(lexer);
            if (lexer->lookahead == '!') {
                advance(lexer);
                return scan_comment(lexer);
            }
            break;
        case '/':
            if (valid_symbols[SELF_CLOSING_TAG_DELIMITER]) {
                return scan_self_closing_tag_delimiter(tags, lexer);
            }
            break;
        case '\0':
            break;
        default:
            if (valid_symbols[GENERIC_START_TAG_NAME] ||
                valid_symbols[FACELETS_START_TAG_NAME] ||
                valid_symbols[JSF_HTML_START_TAG_NAME] ||
                valid_symbols[JSF_CORE_START_TAG_NAME] ||
                valid_symbols[COMPOSITE_START_TAG_NAME] ||
                valid_symbols[FACES_START_TAG_NAME] ||
                valid_symbols[PRIMEFACES_START_TAG_NAME] ||
                valid_symbols[PRIMEFACES_EXTENSIONS_START_TAG_NAME] ||
                valid_symbols[JSTL_START_TAG_NAME] ||
                valid_symbols[QUALIFIED_START_TAG_NAME]) {
                return scan_start_tag_name(tags, lexer, valid_symbols);
            }
            if (valid_symbols[GENERIC_END_TAG_NAME] ||
                valid_symbols[FACELETS_END_TAG_NAME] ||
                valid_symbols[JSF_HTML_END_TAG_NAME] ||
                valid_symbols[JSF_CORE_END_TAG_NAME] ||
                valid_symbols[COMPOSITE_END_TAG_NAME] ||
                valid_symbols[FACES_END_TAG_NAME] ||
                valid_symbols[PRIMEFACES_END_TAG_NAME] ||
                valid_symbols[PRIMEFACES_EXTENSIONS_END_TAG_NAME] ||
                valid_symbols[JSTL_END_TAG_NAME] ||
                valid_symbols[QUALIFIED_END_TAG_NAME]) {
                return scan_end_tag_name(tags, lexer, valid_symbols);
            }
    }

    return false;
}

void *tree_sitter_java_faces_frontend_external_scanner_create(void) {
    Vector *tags = (Vector *)ts_calloc(1, sizeof(Vector));
    if (tags == NULL) abort();
    array_init(tags);
    return tags;
}

void tree_sitter_java_faces_frontend_external_scanner_destroy(void *payload) {
    Vector *tags = (Vector *)payload;
    for (uint32_t index = 0; index < tags->size; ++index) {
        array_delete(array_get(tags, index));
    }
    array_delete(tags);
    ts_free(tags);
}

unsigned tree_sitter_java_faces_frontend_external_scanner_serialize(
    void *payload,
    char *buffer
) {
    Vector *tags = (Vector *)payload;
    const uint32_t tag_count = tags->size > UINT16_MAX ? UINT16_MAX : tags->size;
    uint32_t serialized_count = 0;
    uint32_t size = sizeof(tag_count) * 2;

    for (; serialized_count < tag_count; ++serialized_count) {
        const String *tag = array_get(tags, serialized_count);
        const uint32_t name_length = tag->size > UINT8_MAX ? UINT8_MAX : tag->size;
        if (size + 1 + name_length >= TREE_SITTER_SERIALIZATION_BUFFER_SIZE) break;
        buffer[size++] = (char)name_length;
        if (name_length > 0) {
            memcpy(&buffer[size], tag->contents, name_length);
            size += name_length;
        }
    }

    memcpy(&buffer[0], &serialized_count, sizeof(serialized_count));
    memcpy(&buffer[sizeof(serialized_count)], &tag_count, sizeof(tag_count));
    return size;
}

void tree_sitter_java_faces_frontend_external_scanner_deserialize(
    void *payload,
    const char *buffer,
    unsigned length
) {
    Vector *tags = (Vector *)payload;
    for (uint32_t index = 0; index < tags->size; ++index) {
        array_delete(array_get(tags, index));
    }
    array_clear(tags);

    if (length < sizeof(uint32_t) * 2) return;

    uint32_t serialized_count = 0;
    uint32_t tag_count = 0;
    uint32_t size = 0;
    memcpy(&serialized_count, &buffer[size], sizeof(serialized_count));
    size += sizeof(serialized_count);
    memcpy(&tag_count, &buffer[size], sizeof(tag_count));
    size += sizeof(tag_count);

    array_reserve(tags, tag_count);
    uint32_t index = 0;
    for (; index < serialized_count && size < length; ++index) {
        String tag = array_new();
        const uint8_t name_length = (uint8_t)buffer[size++];
        array_reserve(&tag, name_length);
        if (name_length > 0 && size + name_length <= length) {
            memcpy(tag.contents, &buffer[size], name_length);
            tag.size = name_length;
            size += name_length;
        }
        array_push(tags, tag);
    }
    for (; index < tag_count; ++index) {
        String tag = array_new();
        array_push(tags, tag);
    }
}
