namespace FastParse;

/// <summary>
/// Result returned after loading a native FastParse language extension.
/// </summary>
public sealed class LanguageExtensionLoadResult
{
    /// <summary>Canonical parse language registered by the extension.</summary>
    public string Language { get; init; } = string.Empty;

    /// <summary>Human-readable language name from the extension descriptor.</summary>
    public string DisplayName { get; init; } = string.Empty;
}
