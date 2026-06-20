namespace FastParse;

public sealed class FastParseBinaryNode
{
    public ulong? Id { get; init; }

    public ulong? ParentId { get; init; }

    public string? Rule { get; init; }

    public byte[]? Text { get; init; }

    public ulong? StartLine { get; init; }

    public ulong? StartColumn { get; init; }

    public ulong? EndLine { get; init; }

    public ulong? EndColumn { get; init; }

    public ulong? StartByte { get; init; }

    public ulong? EndByte { get; init; }

    public ulong? ChildCount { get; init; }

    public IReadOnlyList<FastParseBinaryChild> Children { get; init; } = Array.Empty<FastParseBinaryChild>();
}
