namespace FastParse;

public sealed class ParseSummary
{
    public ParseSummary(ulong outputLength, ulong nodeCount, FastParseFormat format)
    {
        OutputLength = outputLength;
        NodeCount = nodeCount;
        Format = format;
    }

    public ulong OutputLength { get; }

    public ulong NodeCount { get; }

    public FastParseFormat Format { get; }
}
