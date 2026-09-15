package dev.fastparse;

/** Counts and output length returned without exposing raw native pointers. */
public final class ParseSummary {
    private final long outputLength;
    private final long nodeCount;
    private final FastParseFormat format;

    public ParseSummary(long outputLength, long nodeCount, FastParseFormat format) {
        this.outputLength = outputLength;
        this.nodeCount = nodeCount;
        this.format = format;
    }

    public long getOutputLength() { return outputLength; }
    public long getNodeCount() { return nodeCount; }
    public FastParseFormat getFormat() { return format; }
}
