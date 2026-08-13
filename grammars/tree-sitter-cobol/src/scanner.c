#include <tree_sitter/parser.h>
#include <wctype.h>

enum TokenType {
    WHITE_SPACES,
    LINE_PREFIX_COMMENT,
    LINE_SUFFIX_COMMENT,
    LINE_COMMENT,
    COMMENT_ENTRY,
    multiline_string,
    FIXED_FORMAT_INTEGER_VALUE,
    FIXED_FORMAT_PERIOD,
    FIXED_FORMAT_PICTURE_X,
    FIXED_FORMAT_PICTURE_9,
    FIXED_FORMAT_PICTURE_EDIT,
    DATE_FORMAT_CLAUSE,
};

void *tree_sitter_COBOL_external_scanner_create() {
    return NULL;
}

static bool is_white_space(int c) {
    return iswspace(c) || c == ';' || c == ',';
}

static bool is_digit(int c) {
    return c >= '0' && c <= '9';
}

static bool is_ascii_alpha(int c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}

static bool is_date_format_space(int c) {
    return c == ' ' || c == '\t';
}

static bool is_date_format_char(int c) {
    return is_ascii_alpha(c) || is_digit(c) || c == '-';
}

static bool is_data_clause_delimiter(int c) {
    return c == 0 || c == '\n' || c == '\r' || c == ' ' || c == '\t' ||
           c == ';' || c == '.';
}

static bool char_equals_case_insensitive(int c, char expected_lower) {
    return c == expected_lower || c == expected_lower - ('a' - 'A');
}

static bool scan_case_insensitive_word(TSLexer *lexer, const char *word) {
    for(int i = 0; word[i] != 0; i++) {
        if(!char_equals_case_insensitive(lexer->lookahead, word[i])) {
            return false;
        }
        lexer->advance(lexer, false);
    }
    return true;
}

static bool is_picture_count_start(int c) {
    return c == '(';
}

static bool is_picture_9_unit_char(int c) {
    return c == '9' || c == 'p' || c == 'P';
}

static bool is_picture_x_unit_char(int c) {
    return c == 'x' || c == 'X';
}

static bool is_picture_z_unit_char(int c) {
    return c == 'z' || c == 'Z';
}

static bool is_picture_edit_char(int c) {
    return is_picture_x_unit_char(c) || is_picture_9_unit_char(c) ||
           is_picture_z_unit_char(c) || c == 'a' || c == 'A' ||
           c == 'b' || c == 'B' || c == 'v' || c == 'V' ||
           c == 'w' || c == 'W' || c == 'c' || c == 'C' ||
           c == 'r' || c == 'R' || c == 'd' || c == 'D' ||
           is_digit(c) || c == '(' || c == ')' || c == '$' ||
           c == '/' || c == ',' || c == '*' || c == '+' ||
           c == '<' || c == '>' || c == '-' || c == '.';
}

static bool is_picture_editing_char(int c) {
    return is_picture_z_unit_char(c) || c == '$' || c == '/' || c == ',' ||
           c == '*' || c == '+' || c == '<' || c == '>' || c == '-' ||
           c == '.';
}

typedef struct {
    int count;
    int first_char;
    bool first_has_count;
    int first_count_value;
} PictureUnitScan;

static bool is_fixed_format_statement_period(TSLexer *lexer) {
    return lexer->lookahead == '.' && lexer->get_column(lexer) == 71;
}

static bool is_simple_picture_delimiter(TSLexer *lexer) {
    int c = lexer->lookahead;
    return c == 0 || c == '\n' || c == '\r' || c == ' ' || c == '\t' ||
           c == ';' || c == '.';
}

static bool scan_picture_count(TSLexer *lexer, bool *has_count, int *count_value) {
    *has_count = false;
    *count_value = 0;

    if(!is_picture_count_start(lexer->lookahead)) {
        return true;
    }

    *has_count = true;
    lexer->advance(lexer, false);
    if(!is_digit(lexer->lookahead)) {
        return false;
    }

    while(is_digit(lexer->lookahead)) {
        *count_value = (*count_value * 10) + (lexer->lookahead - '0');
        lexer->advance(lexer, false);
    }

    if(lexer->lookahead != ')') {
        return false;
    }

    lexer->advance(lexer, false);
    return true;
}

static PictureUnitScan scan_repeated_picture_units(TSLexer *lexer, bool (*is_unit_char)(int)) {
    PictureUnitScan scan = {0, 0, false, 0};
    while(is_unit_char(lexer->lookahead)) {
        int unit_char = lexer->lookahead;
        bool has_count = false;
        int count_value = 0;
        lexer->advance(lexer, false);
        if(!scan_picture_count(lexer, &has_count, &count_value)) {
            scan.count = -1;
            return scan;
        }
        if(scan.count == 0) {
            scan.first_char = unit_char;
            scan.first_has_count = has_count;
            scan.first_count_value = count_value;
        }
        scan.count++;
    }
    return scan;
}

static bool accept_simple_picture_token(TSLexer *lexer, int token_type) {
    if(!is_simple_picture_delimiter(lexer)) {
        return false;
    }

    lexer->mark_end(lexer);

    if(lexer->lookahead == '.') {
        int period_column = lexer->get_column(lexer);
        lexer->advance(lexer, false);
        if(period_column != 71 && is_digit(lexer->lookahead)) {
            return false;
        }
    }

    lexer->result_symbol = token_type;
    return true;
}

static bool scan_fixed_format_picture_x(TSLexer *lexer) {
    if(lexer->get_column(lexer) < 60) {
        return false;
    }

    if(!is_picture_x_unit_char(lexer->lookahead)) {
        return false;
    }

    PictureUnitScan units = scan_repeated_picture_units(lexer, is_picture_x_unit_char);
    if(units.count <= 0) {
        return false;
    }

    return accept_simple_picture_token(lexer, FIXED_FORMAT_PICTURE_X);
}

static bool scan_picture_9_body(TSLexer *lexer, bool *plain_single_count_3) {
    *plain_single_count_3 = false;
    bool has_sign = false;

    if(lexer->lookahead == 's' || lexer->lookahead == 'S') {
        has_sign = true;
        lexer->advance(lexer, false);
    }

    if(lexer->lookahead == 'v' || lexer->lookahead == 'V') {
        lexer->advance(lexer, false);
        PictureUnitScan after_v_units = scan_repeated_picture_units(lexer, is_picture_9_unit_char);
        return after_v_units.count >= 0;
    }

    PictureUnitScan leading_units = scan_repeated_picture_units(lexer, is_picture_9_unit_char);
    if(leading_units.count <= 0) {
        return false;
    }

    if(lexer->lookahead == 'v' || lexer->lookahead == 'V') {
        lexer->advance(lexer, false);
        PictureUnitScan after_v_units = scan_repeated_picture_units(lexer, is_picture_9_unit_char);
        return after_v_units.count >= 0;
    }

    if(is_picture_z_unit_char(lexer->lookahead)) {
        PictureUnitScan z_units = scan_repeated_picture_units(lexer, is_picture_z_unit_char);
        return z_units.count > 0;
    }

    *plain_single_count_3 = !has_sign &&
        leading_units.count == 1 &&
        leading_units.first_char == '9' &&
        leading_units.first_has_count &&
        leading_units.first_count_value == 3;
    return true;
}

static bool scan_fixed_format_picture_9(TSLexer *lexer) {
    if(lexer->get_column(lexer) < 60) {
        return false;
    }

    if(!is_picture_9_unit_char(lexer->lookahead) &&
       lexer->lookahead != 's' && lexer->lookahead != 'S' &&
       lexer->lookahead != 'v' && lexer->lookahead != 'V') {
        return false;
    }

    bool plain_single_count_3 = false;
    if(!scan_picture_9_body(lexer, &plain_single_count_3)) {
        return false;
    }

    return accept_simple_picture_token(lexer, FIXED_FORMAT_PICTURE_9);
}

static bool scan_fixed_format_picture_edit(TSLexer *lexer) {
    int start_column = lexer->get_column(lexer);
    if(start_column < 40 || start_column >= 71) {
        return false;
    }

    bool has_char = false;
    bool has_editing_char = false;
    while(lexer->get_column(lexer) < 71 && is_picture_edit_char(lexer->lookahead)) {
        has_char = true;
        if(is_picture_editing_char(lexer->lookahead)) {
            has_editing_char = true;
        }
        lexer->advance(lexer, false);
    }

    if(!has_char || !has_editing_char || !is_fixed_format_statement_period(lexer)) {
        return false;
    }

    lexer->result_symbol = FIXED_FORMAT_PICTURE_EDIT;
    lexer->mark_end(lexer);
    return true;
}

static bool scan_date_format_clause(TSLexer *lexer) {
    if(!char_equals_case_insensitive(lexer->lookahead, 'd')) {
        return false;
    }

    if(!scan_case_insensitive_word(lexer, "date")) {
        return false;
    }

    if(!is_date_format_space(lexer->lookahead)) {
        return false;
    }

    while(is_date_format_space(lexer->lookahead)) {
        lexer->advance(lexer, false);
    }

    if(!scan_case_insensitive_word(lexer, "format")) {
        return false;
    }

    if(!is_date_format_space(lexer->lookahead)) {
        return false;
    }

    while(is_date_format_space(lexer->lookahead)) {
        lexer->advance(lexer, false);
    }

    bool has_format = false;
    while(is_date_format_char(lexer->lookahead)) {
        has_format = true;
        lexer->advance(lexer, false);
    }

    if(!has_format || !is_data_clause_delimiter(lexer->lookahead)) {
        return false;
    }

    lexer->result_symbol = DATE_FORMAT_CLAUSE;
    lexer->mark_end(lexer);
    return true;
}

const int number_of_comment_entry_keywords = 9;
char* any_content_keyword[] = {
    "author",
    "installlation",
    "date-written",
    "date-compiled",
    "security",
    "identification division",
    "environment division",
    "data division",
    "procedure division",
};

static bool start_with_word( TSLexer *lexer, char *words[], int number_of_words) {
    while(lexer->lookahead == ' ' || lexer->lookahead == '\t') {
        lexer->advance(lexer, true);
    }

    char *keyword_pointer[number_of_words];
    bool continue_check[number_of_words];
    for(int i=0; i<number_of_words; ++i) {
        keyword_pointer[i] = words[i];
        continue_check[i] = true;
    }

    while(true) {
        // At the end of the line
        if(lexer->get_column(lexer) > 71 || lexer->lookahead == '\n' || lexer->lookahead == 0) {
            return false;
        }

        // If all keyword matching fails, move to the end of the line
        bool all_match_failed = true;
        for(int i=0; i<number_of_words; ++i) {
            if(continue_check[i]) {
                all_match_failed = false;
            }
        }

        if(all_match_failed) {
            for(; lexer->get_column(lexer) < 71 && lexer->lookahead != '\n' && lexer->lookahead != 0;
            lexer->advance(lexer, true)) {
            }
            return false;
        }

        // If the head of the line matches any of specified keywords, return true;
        char c = lexer->lookahead;
        for(int i=0; i<number_of_words; ++i) {
            if(*(keyword_pointer[i]) == 0 && continue_check[i]) {
                return true;
            }
        }

        // matching keywords
        for(int i=0; i<number_of_words; ++i) {
            char k = *(keyword_pointer[i]);
            if(continue_check[i]) {
                continue_check[i] = c == towupper(k) || c == towlower(k);
            }
            (keyword_pointer[i])++;
        }

        // next character
        lexer->advance(lexer, true);
    }

    return false;
}

bool tree_sitter_COBOL_external_scanner_scan(void *payload, TSLexer *lexer,
                                            const bool *valid_symbols) {
    if(lexer->lookahead == 0) {
        return false;
    }

    if(valid_symbols[WHITE_SPACES]) {
        if(is_white_space(lexer->lookahead)) {
            while(is_white_space(lexer->lookahead)) {
                lexer->advance(lexer, true);
            }
            lexer->result_symbol = WHITE_SPACES;
            lexer->mark_end(lexer);
            return true;
        }

        if(lexer->get_column(lexer) == 6 && (lexer->lookahead == 'D' || lexer->lookahead == 'd')) {
            lexer->advance(lexer, true);
            lexer->result_symbol = WHITE_SPACES;
            lexer->mark_end(lexer);
            return true;
        }
    }

    if(valid_symbols[FIXED_FORMAT_PERIOD]) {
        if(is_fixed_format_statement_period(lexer)) {
            lexer->advance(lexer, false);
            lexer->result_symbol = FIXED_FORMAT_PERIOD;
            lexer->mark_end(lexer);
            return true;
        }
    }

    if(valid_symbols[FIXED_FORMAT_PICTURE_X]) {
        if(scan_fixed_format_picture_x(lexer)) {
            return true;
        }
    }

    if(valid_symbols[FIXED_FORMAT_PICTURE_9]) {
        if(scan_fixed_format_picture_9(lexer)) {
            return true;
        }
    }

    if(valid_symbols[FIXED_FORMAT_PICTURE_EDIT]) {
        if(scan_fixed_format_picture_edit(lexer)) {
            return true;
        }
    }

    if(valid_symbols[DATE_FORMAT_CLAUSE]) {
        if(scan_date_format_clause(lexer)) {
            return true;
        }
    }

    if(valid_symbols[FIXED_FORMAT_INTEGER_VALUE]) {
        int start_column = lexer->get_column(lexer);
        if(start_column == 70 && is_digit(lexer->lookahead)) {
            lexer->advance(lexer, false);
            lexer->result_symbol = FIXED_FORMAT_INTEGER_VALUE;
            lexer->mark_end(lexer);
            return true;
        }

        if(start_column >= 60 && start_column < 70 && is_digit(lexer->lookahead)) {
            bool has_digit = false;
            while(lexer->get_column(lexer) <= 70 && is_digit(lexer->lookahead)) {
                has_digit = true;
                lexer->advance(lexer, false);
            }
            if(has_digit && is_fixed_format_statement_period(lexer)) {
                lexer->result_symbol = FIXED_FORMAT_INTEGER_VALUE;
                lexer->mark_end(lexer);
                return true;
            }
        }

        if(start_column >= 60 && start_column < 70 && (lexer->lookahead == '+' || lexer->lookahead == '-')) {
            bool has_digit = false;
            lexer->advance(lexer, false);
            while(lexer->get_column(lexer) <= 70 && is_digit(lexer->lookahead)) {
                has_digit = true;
                lexer->advance(lexer, false);
            }
            if(has_digit) {
                lexer->result_symbol = FIXED_FORMAT_INTEGER_VALUE;
                lexer->mark_end(lexer);
                return true;
            }
        }
    }

    if(valid_symbols[LINE_PREFIX_COMMENT] && lexer->get_column(lexer) <= 5) {
        while(lexer->get_column(lexer) <= 5) {
            lexer->advance(lexer, true);
        }
        lexer->result_symbol = LINE_PREFIX_COMMENT;
        lexer->mark_end(lexer);
        return true;
    }

    if(valid_symbols[LINE_COMMENT]) {
        if(lexer->get_column(lexer) == 6) {
            if(lexer->lookahead == '*' || lexer->lookahead == '/') {
                while(lexer->lookahead != '\n' && lexer->lookahead != 0) {
                    lexer->advance(lexer, true);
                }
                lexer->result_symbol = LINE_COMMENT;
                lexer->mark_end(lexer);
                return true;
            } else {
                lexer->advance(lexer, true);
                lexer->mark_end(lexer);
                return false;
            }
        }
    }

    if(valid_symbols[LINE_SUFFIX_COMMENT]) {
        if(lexer->get_column(lexer) >= 72) {
            while(lexer->lookahead != '\n' && lexer->lookahead != 0) {
                lexer->advance(lexer, true);
            }
            lexer->result_symbol = LINE_SUFFIX_COMMENT;
            lexer->mark_end(lexer);
            return true;
        }
    }

    if(valid_symbols[COMMENT_ENTRY]) {
        if(!start_with_word(lexer, any_content_keyword, number_of_comment_entry_keywords)) {
            lexer->mark_end(lexer);
            lexer->result_symbol = COMMENT_ENTRY;
            return true;
        } else {
            return false;
        }
    }

    if(valid_symbols[multiline_string]) {
        int quote = lexer->lookahead;

        if(quote != '"' && quote != '\'') {
            return false;
        }

        while(true) {
            if(lexer->lookahead != quote) {
                return false;
            }
            lexer->advance(lexer, false);
            while(lexer->lookahead != quote && lexer->lookahead != 0 && lexer->get_column(lexer) < 72) {
                lexer->advance(lexer, false);
            }
            if(lexer->lookahead == quote) {
                lexer->advance(lexer, false);
                lexer->mark_end(lexer);
                if(lexer->lookahead == quote && lexer->get_column(lexer) < 72) {
                    continue;
                }
                lexer->result_symbol = multiline_string;
                return true;
            }
            while(lexer->lookahead != 0 && lexer->lookahead != '\n') {
                lexer->advance(lexer, true);
            }
            if(lexer->lookahead == 0) {
                return false;
            }
            lexer->advance(lexer, true);
            int i;
            for(i=0; i<=5; ++i) {
                if(lexer->lookahead == 0 || lexer->lookahead == '\n') {
                    return false;
                }
                lexer->advance(lexer, true);
            }

            if(lexer->lookahead != '-') {
                return false;
            }

            lexer->advance(lexer, true);
            while(lexer->lookahead == ' ' && lexer->get_column(lexer) < 72) {
                lexer->advance(lexer, true);
            }
        }
    }

    return false;
}

unsigned tree_sitter_COBOL_external_scanner_serialize(void *payload, char *buffer) {
    return 0;
}

void tree_sitter_COBOL_external_scanner_deserialize(void *payload, const char *buffer, unsigned length) {
}

void tree_sitter_COBOL_external_scanner_destroy(void *payload) {
}
