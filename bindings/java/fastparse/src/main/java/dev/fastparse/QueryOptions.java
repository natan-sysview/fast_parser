package dev.fastparse;

/** Immutable options passed to a FastParse Tree-sitter query call. */
public final class QueryOptions {
    private final String language;
    private final FastParseFormat format;
    private final long fields;
    private final long maxMatches;
    private final long maxCaptures;
    private final boolean includePattern;
    private final boolean pretty;
    private final FastParseNormalization normalization;

    private QueryOptions(Builder builder) {
        this.language = builder.language;
        this.format = builder.format;
        this.fields = builder.fields;
        this.maxMatches = builder.maxMatches;
        this.maxCaptures = builder.maxCaptures;
        this.includePattern = builder.includePattern;
        this.pretty = builder.pretty;
        this.normalization = builder.normalization;
    }

    public static Builder builder() { return new Builder(); }

    public String getLanguage() { return language; }
    public FastParseFormat getFormat() { return format; }
    public long getFields() { return fields; }
    public long getMaxMatches() { return maxMatches; }
    public long getMaxCaptures() { return maxCaptures; }
    public boolean isIncludePattern() { return includePattern; }
    public boolean isPretty() { return pretty; }
    public FastParseNormalization getNormalization() { return normalization; }

    public static final class Builder {
        private String language = "java";
        private FastParseFormat format = FastParseFormat.JSON;
        private long fields = 0L;
        private long maxMatches;
        private long maxCaptures;
        private boolean includePattern = true;
        private boolean pretty;
        private FastParseNormalization normalization = FastParseNormalization.AUTO_SAFE;

        public Builder language(String language) { this.language = language == null || language.isEmpty() ? "java" : language; return this; }
        public Builder format(FastParseFormat format) { this.format = format == null ? FastParseFormat.JSON : format; return this; }
        public Builder fields(long fields) { this.fields = fields; return this; }
        public Builder fields(FastParseField... fields) { this.fields = FastParseField.maskOf(fields); return this; }
        public Builder maxMatches(long maxMatches) { this.maxMatches = Math.max(0L, maxMatches); return this; }
        public Builder maxCaptures(long maxCaptures) { this.maxCaptures = Math.max(0L, maxCaptures); return this; }
        public Builder includePattern(boolean includePattern) { this.includePattern = includePattern; return this; }
        public Builder pretty(boolean pretty) { this.pretty = pretty; return this; }
        public Builder normalization(FastParseNormalization normalization) { this.normalization = normalization == null ? FastParseNormalization.AUTO_SAFE : normalization; return this; }
        public QueryOptions build() { return new QueryOptions(this); }
    }
}
