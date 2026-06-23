using System.Text;
using System.Text.Json;

namespace FastParse;

/// <summary>
/// Full parse result with output bytes copied into managed memory.
/// </summary>
public sealed class ParseResult
{
    /// <summary>
    /// Creates a parse result from native output bytes.
    /// </summary>
    /// <param name="data">Output bytes copied from native memory.</param>
    /// <param name="nodeCount">Number of nodes matched by the parse options.</param>
    /// <param name="format">Output format used for <paramref name="data"/>.</param>
    public ParseResult(byte[] data, ulong nodeCount, FastParseFormat format)
    {
        Data = data;
        NodeCount = nodeCount;
        Format = format;
    }

    /// <summary>Output bytes copied from native memory.</summary>
    public byte[] Data { get; }

    /// <summary>Number of nodes matched by the parse options.</summary>
    public ulong NodeCount { get; }

    /// <summary>Output format used for <see cref="Data"/>.</summary>
    public FastParseFormat Format { get; }

    /// <summary>Interprets <see cref="Data"/> as UTF-8 text.</summary>
    public string Text => Encoding.UTF8.GetString(Data);

    /// <summary>
    /// Parses <see cref="Data"/> as a JSON document.
    /// </summary>
    /// <returns>A JSON document owned by the caller.</returns>
    public JsonDocument JsonDocument()
    {
        return System.Text.Json.JsonDocument.Parse(Data);
    }
}
