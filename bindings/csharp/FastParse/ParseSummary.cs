namespace FastParse;

/// <summary>
/// Summary parse result that avoids copying native output bytes.
/// </summary>
public sealed class ParseSummary
{
    /// <summary>
    /// Creates a summary result.
    /// </summary>
    /// <param name="outputLength">Number of bytes the native parser produced.</param>
    /// <param name="nodeCount">Number of nodes matched by the parse options.</param>
    /// <param name="format">Output format requested.</param>
    public ParseSummary(ulong outputLength, ulong nodeCount, FastParseFormat format)
    {
        OutputLength = outputLength;
        NodeCount = nodeCount;
        Format = format;
    }

    /// <summary>Number of bytes the native parser produced.</summary>
    public ulong OutputLength { get; }

    /// <summary>Number of nodes matched by the parse options.</summary>
    public ulong NodeCount { get; }

    /// <summary>Output format requested.</summary>
    public FastParseFormat Format { get; }
}
