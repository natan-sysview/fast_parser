namespace FastParse;

/// <summary>
/// Decoded FastParse binary MessagePack document.
/// </summary>
public sealed class FastParseBinaryDocument
{
    /// <summary>Binary format marker, currently <c>tsmp-binary</c>.</summary>
    public string Format { get; init; } = string.Empty;

    /// <summary>Binary schema version.</summary>
    public ulong SchemaVersion { get; init; }

    /// <summary>Language grammar used by the native parser.</summary>
    public string Language { get; init; } = string.Empty;

    /// <summary>Whether Tree-sitter reported ERROR or MISSING nodes anywhere in the parse tree.</summary>
    public bool? HasErrors { get; init; }

    /// <summary>Number of ERROR nodes in the full parse tree when diagnostics were requested.</summary>
    public ulong? ErrorNodeCount { get; init; }

    /// <summary>Number of MISSING nodes in the full parse tree when diagnostics were requested.</summary>
    public ulong? MissingNodeCount { get; init; }

    /// <summary>Total bytes covered by ERROR nodes when diagnostics were requested.</summary>
    public ulong? ErrorByteCount { get; init; }

    /// <summary>Decoded AST nodes included in the binary payload.</summary>
    public IReadOnlyList<FastParseBinaryNode> Nodes { get; init; } = Array.Empty<FastParseBinaryNode>();

    /// <summary>Total node count reported by the native parser.</summary>
    public ulong NodeCount { get; init; }
}
