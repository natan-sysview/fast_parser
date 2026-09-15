package dev.fastparse;

/** Bit flags controlling which fields FastParse includes in AST/query output. */
public enum FastParseField {
    ID(1L << 0),
    PARENT_ID(1L << 1),
    RULE(1L << 2),
    TEXT(1L << 3),
    RANGE(1L << 4),
    BYTE_RANGE(1L << 5),
    CHILD_COUNT(1L << 6),
    CHILDREN(1L << 7),
    DIAGNOSTICS(1L << 8),
    CAPTURE_NAME(1L << 9),
    PATTERN_INDEX(1L << 10),
    FIELD_NAME(1L << 11),
    CHILD_INDEX(1L << 12),
    NAMED(1L << 13),
    DEPTH(1L << 14),
    ALL(0xFFFFFFFFL);

    private final long mask;

    FastParseField(long mask) {
        this.mask = mask;
    }

    public long mask() {
        return mask;
    }

    public static long maskOf(FastParseField... fields) {
        if (fields == null || fields.length == 0) {
            return 0L;
        }
        long value = 0L;
        for (FastParseField field : fields) {
            if (field != null) {
                value |= field.mask;
            }
        }
        return value;
    }
}
