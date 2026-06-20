using System.Text;
using System.Text.Json;

namespace FastParse;

public sealed class ParseResult
{
    public ParseResult(byte[] data, ulong nodeCount, FastParseFormat format)
    {
        Data = data;
        NodeCount = nodeCount;
        Format = format;
    }

    public byte[] Data { get; }

    public ulong NodeCount { get; }

    public FastParseFormat Format { get; }

    public string Text => Encoding.UTF8.GetString(Data);

    public JsonDocument JsonDocument()
    {
        return System.Text.Json.JsonDocument.Parse(Data);
    }
}
