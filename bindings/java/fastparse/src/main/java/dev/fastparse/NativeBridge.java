package dev.fastparse;

final class NativeBridge {
    private NativeBridge() {}

    static native void nativeInitialize(String coreLibraryPath);
    static native String nativeVersion();
    static native boolean nativeLanguageAvailable(String language);
    static native String[] nativeLoadLanguageExtension(String path);

    static native ParseResult nativeParse(
            byte[] source,
            String language,
            int format,
            String includeRules,
            long fields,
            boolean includeTokens,
            boolean pretty,
            int normalization);

    static native ParseResult nativeQuery(
            byte[] source,
            byte[] query,
            String language,
            int format,
            long fields,
            long maxMatches,
            long maxCaptures,
            boolean includePattern,
            boolean pretty,
            int normalization);
}
