namespace FastParse;

/// <summary>
/// Options passed to a FastParse parse call.
/// </summary>
public sealed class ParseOptions
{
    /// <summary>
    /// Language grammar to use. The current preview package supports <c>java</c>.
    /// </summary>
    public string Language { get; init; } = "java";

    /// <summary>
    /// Output format to produce.
    /// </summary>
    public FastParseFormat Format { get; init; } = FastParseFormat.Json;

    /// <summary>
    /// Optional pipe-delimited Tree-sitter rule names to include, for example <c>class_declaration|method_declaration</c>.
    /// Leave null or empty to include the full AST.
    /// </summary>
    public string? IncludeRules { get; init; }

    /// <summary>
    /// Field flags to include in output. <see cref="FastParseField.DefaultAll"/> uses the native default.
    /// </summary>
    public FastParseField Fields { get; init; } = FastParseField.DefaultAll;

    /// <summary>
    /// Whether token nodes should be included when supported by the native parser.
    /// </summary>
    public bool IncludeTokens { get; init; }

    /// <summary>
    /// Whether JSON output should be pretty-printed.
    /// </summary>
    public bool Pretty { get; init; }

    /// <summary>
    /// Default JSON parse options that return the exploratory AST output.
    /// </summary>
    public static ParseOptions JsonAll { get; } = new();
}
