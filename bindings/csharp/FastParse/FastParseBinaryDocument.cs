namespace FastParse;

public sealed class FastParseBinaryDocument
{
    public string Format { get; init; } = string.Empty;

    public ulong SchemaVersion { get; init; }

    public string Language { get; init; } = string.Empty;

    public IReadOnlyList<FastParseBinaryNode> Nodes { get; init; } = Array.Empty<FastParseBinaryNode>();

    public ulong NodeCount { get; init; }
}
