package dev.fastparse;

/** Result returned after loading a FastParse language extension. */
public final class LanguageExtensionLoadResult {
    private final String language;
    private final String displayName;

    public LanguageExtensionLoadResult(String language, String displayName) {
        this.language = language == null ? "" : language;
        this.displayName = displayName == null ? "" : displayName;
    }

    public String getLanguage() { return language; }
    public String getDisplayName() { return displayName; }
}
