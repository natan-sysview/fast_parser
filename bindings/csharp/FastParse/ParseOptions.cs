namespace FastParse;

public sealed class ParseOptions
{
    public string Language { get; init; } = "java";

    public FastParseFormat Format { get; init; } = FastParseFormat.Json;

    public string? IncludeRules { get; init; }

    public FastParseField Fields { get; init; } = FastParseField.DefaultAll;

    public bool IncludeTokens { get; init; }

    public bool Pretty { get; init; }

    public static ParseOptions JsonAll { get; } = new();
}
