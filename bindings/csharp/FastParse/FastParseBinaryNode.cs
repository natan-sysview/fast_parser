namespace FastParse;

/// <summary>
/// Decoded AST node from FastParse binary MessagePack output.
/// </summary>
public sealed class FastParseBinaryNode
{
    /// <summary>Node id when requested.</summary>
    public ulong? Id { get; init; }

    /// <summary>Parent node id when requested.</summary>
    public ulong? ParentId { get; init; }

    /// <summary>Tree-sitter grammar rule name when requested.</summary>
    public string? Rule { get; init; }

    /// <summary>Original source bytes for the node when requested.</summary>
    public byte[]? Text { get; init; }

    /// <summary>Start line when requested.</summary>
    public ulong? StartLine { get; init; }

    /// <summary>Start column when requested.</summary>
    public ulong? StartColumn { get; init; }

    /// <summary>End line when requested.</summary>
    public ulong? EndLine { get; init; }

    /// <summary>End column when requested.</summary>
    public ulong? EndColumn { get; init; }

    /// <summary>Start byte offset when requested.</summary>
    public ulong? StartByte { get; init; }

    /// <summary>End byte offset when requested.</summary>
    public ulong? EndByte { get; init; }

    /// <summary>Child count when requested.</summary>
    public ulong? ChildCount { get; init; }

    /// <summary>Child summaries when requested.</summary>
    public IReadOnlyList<FastParseBinaryChild> Children { get; init; } = Array.Empty<FastParseBinaryChild>();
}
