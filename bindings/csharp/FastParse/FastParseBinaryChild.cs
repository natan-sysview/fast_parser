namespace FastParse;

/// <summary>
/// Decoded child summary from FastParse binary MessagePack output.
/// </summary>
public sealed class FastParseBinaryChild
{
    /// <summary>Child grammar rule when requested.</summary>
    public string? Rule { get; init; }

    /// <summary>Child source bytes when requested.</summary>
    public byte[]? Text { get; init; }
}
