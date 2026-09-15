package dev.fastparse;

import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;

/** High-level Java client for the FastParse native C ABI. */
public final class FastParseClient implements AutoCloseable {
    private boolean closed;

    private FastParseClient(String coreLibraryPath, String jniLibraryPath) {
        NativeLibraryLoader.load(coreLibraryPath, jniLibraryPath);
    }

    /** Open FastParse using bundled package-manager native libraries or environment overrides. */
    public static FastParseClient open() {
        return new FastParseClient(null, null);
    }

    /** Open FastParse using an explicit core library path and bundled/overridden JNI bridge path. */
    public static FastParseClient open(String coreLibraryPath) {
        return new FastParseClient(coreLibraryPath, null);
    }

    /** Open FastParse using explicit core and JNI bridge native library paths. */
    public static FastParseClient open(String coreLibraryPath, String jniLibraryPath) {
        return new FastParseClient(coreLibraryPath, jniLibraryPath);
    }

    public String version() {
        ensureOpen();
        return NativeBridge.nativeVersion();
    }

    public String loadedCorePath() {
        ensureOpen();
        return NativeLibraryLoader.loadedCorePath();
    }

    public boolean languageAvailable(String language) {
        ensureOpen();
        return NativeBridge.nativeLanguageAvailable(language);
    }

    public LanguageExtensionLoadResult loadLanguageExtension(String path) {
        ensureOpen();
        String[] values = NativeBridge.nativeLoadLanguageExtension(path);
        String language = values.length > 0 ? values[0] : "";
        String displayName = values.length > 1 ? values[1] : "";
        return new LanguageExtensionLoadResult(language, displayName);
    }

    public ParseResult parseText(String source) {
        return parseText(source, ParseOptions.builder().build(), StandardCharsets.UTF_8);
    }

    public ParseResult parseText(String source, ParseOptions options) {
        return parseText(source, options, StandardCharsets.UTF_8);
    }

    public ParseResult parseText(String source, ParseOptions options, Charset charset) {
        if (source == null) {
            source = "";
        }
        if (charset == null) {
            charset = StandardCharsets.UTF_8;
        }
        return parseBytes(source.getBytes(charset), options);
    }

    public ParseResult parseBytes(byte[] source, ParseOptions options) {
        ensureOpen();
        if (source == null) {
            source = new byte[0];
        }
        if (options == null) {
            options = ParseOptions.builder().build();
        }
        return NativeBridge.nativeParse(source, options.getLanguage(), options.getFormat().nativeValue(),
                options.getIncludeRules(), options.getFields(), options.isIncludeTokens(), options.isPretty(),
                options.getNormalization().nativeValue());
    }

    public ParseResult queryText(String source, String query, QueryOptions options) {
        if (source == null) source = "";
        if (query == null) query = "";
        return queryBytes(source.getBytes(StandardCharsets.UTF_8), query.getBytes(StandardCharsets.UTF_8), options);
    }

    public ParseResult queryBytes(byte[] source, byte[] query, QueryOptions options) {
        ensureOpen();
        if (source == null) source = new byte[0];
        if (query == null) query = new byte[0];
        if (options == null) options = QueryOptions.builder().build();
        return NativeBridge.nativeQuery(source, query, options.getLanguage(), options.getFormat().nativeValue(),
                options.getFields(), options.getMaxMatches(), options.getMaxCaptures(), options.isIncludePattern(),
                options.isPretty(), options.getNormalization().nativeValue());
    }

    @Override
    public void close() {
        closed = true;
    }

    private void ensureOpen() {
        if (closed) {
            throw new IllegalStateException("FastParseClient is closed");
        }
    }
}
