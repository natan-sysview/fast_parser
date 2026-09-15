package dev.fastparse;

/** Immutable options passed to a FastParse parse call. Defaults to full Java JSON AST. */
public final class ParseOptions {
    private final String language;
    private final FastParseFormat format;
    private final String includeRules;
    private final long fields;
    private final boolean includeTokens;
    private final boolean pretty;
    private final FastParseNormalization normalization;

    private ParseOptions(Builder builder) {
        this.language = builder.language;
        this.format = builder.format;
        this.includeRules = builder.includeRules;
        this.fields = builder.fields;
        this.includeTokens = builder.includeTokens;
        this.pretty = builder.pretty;
        this.normalization = builder.normalization;
    }

    public static Builder builder() {
        return new Builder();
    }

    public String getLanguage() { return language; }
    public FastParseFormat getFormat() { return format; }
    public String getIncludeRules() { return includeRules; }
    public long getFields() { return fields; }
    public boolean isIncludeTokens() { return includeTokens; }
    public boolean isPretty() { return pretty; }
    public FastParseNormalization getNormalization() { return normalization; }

    public static final class Builder {
        private String language = "java";
        private FastParseFormat format = FastParseFormat.JSON;
        private String includeRules;
        private long fields = 0L;
        private boolean includeTokens;
        private boolean pretty;
        private FastParseNormalization normalization = FastParseNormalization.AUTO_SAFE;

        public Builder language(String language) {
            this.language = language == null || language.isEmpty() ? "java" : language;
            return this;
        }

        public Builder format(FastParseFormat format) {
            this.format = format == null ? FastParseFormat.JSON : format;
            return this;
        }

        /** Pipe-delimited exact Tree-sitter rule names. Null/empty means full AST. */
        public Builder includeRules(String includeRules) {
            this.includeRules = includeRules == null || includeRules.isEmpty() ? null : includeRules;
            return this;
        }

        /** Native field mask. Zero means native default/all fields. */
        public Builder fields(long fields) {
            this.fields = fields;
            return this;
        }

        public Builder fields(FastParseField... fields) {
            this.fields = FastParseField.maskOf(fields);
            return this;
        }

        public Builder includeTokens(boolean includeTokens) {
            this.includeTokens = includeTokens;
            return this;
        }

        public Builder pretty(boolean pretty) {
            this.pretty = pretty;
            return this;
        }

        public Builder normalization(FastParseNormalization normalization) {
            this.normalization = normalization == null ? FastParseNormalization.AUTO_SAFE : normalization;
            return this;
        }

        public ParseOptions build() {
            return new ParseOptions(this);
        }
    }
}
