namespace FastParse;

/// <summary>
/// Options passed to a FastParse Tree-sitter query call.
/// </summary>
public sealed class QueryOptions
{
    /// <summary>
    /// Language grammar to use. The default package supports <c>java</c>; loaded extensions can add more languages.
    /// </summary>
    public string Language { get; init; } = "java";

    /// <summary>
    /// Output format to produce. Query supports JSON, CSV, binary MessagePack, and stats.
    /// </summary>
    public FastParseFormat Format { get; init; } = FastParseFormat.Json;

    /// <summary>
    /// Field flags to include in capture output. <see cref="FastParseField.DefaultAll"/> uses the native query default.
    /// </summary>
    public FastParseField Fields { get; init; } = FastParseField.DefaultAll;

    /// <summary>
    /// Maximum matches to return. Zero means unlimited.
    /// </summary>
    public nuint MaxMatches { get; init; }

    /// <summary>
    /// Maximum captures to return. Zero means unlimited.
    /// </summary>
    public nuint MaxCaptures { get; init; }

    /// <summary>
    /// Whether patternIndex should be included even when the field mask does not explicitly request it.
    /// </summary>
    public bool IncludePattern { get; init; } = true;

    /// <summary>
    /// Reserved for formatted JSON.
    /// </summary>
    public bool Pretty { get; init; }

    /// <summary>
    /// Source normalization to apply before parsing. AutoSafe applies conservative legacy cleanup for languages such as COBOL.
    /// </summary>
    public FastParseNormalization Normalization { get; init; } = FastParseNormalization.AutoSafe;

    /// <summary>
    /// Default Java query options that return capture name, rule, text, ranges, and pattern index.
    /// </summary>
    public static QueryOptions JsonDefault { get; } = new();
}
