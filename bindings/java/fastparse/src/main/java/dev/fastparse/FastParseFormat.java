package dev.fastparse;

/** Output format produced by FastParse. */
public enum FastParseFormat {
    JSON(1),
    CSV(2),
    STATS(3),
    BINARY(4),
    DIAGNOSTICS(5);

    private final int nativeValue;

    FastParseFormat(int nativeValue) {
        this.nativeValue = nativeValue;
    }

    public int nativeValue() {
        return nativeValue;
    }
}
