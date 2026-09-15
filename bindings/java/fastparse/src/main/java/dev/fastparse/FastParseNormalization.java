package dev.fastparse;

/** Source normalization mode applied before Tree-sitter parsing. */
public enum FastParseNormalization {
    AUTO_SAFE(0),
    NONE(1),
    COBOL_FIXED_LEGACY(2);

    private final int nativeValue;

    FastParseNormalization(int nativeValue) {
        this.nativeValue = nativeValue;
    }

    public int nativeValue() {
        return nativeValue;
    }
}
