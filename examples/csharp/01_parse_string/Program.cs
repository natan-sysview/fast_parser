using System.Text;
using FastParse;

static void Assert(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}

var source = Encoding.UTF8.GetBytes("""
public class Demo {
    public void run() {
        System.out.println("hello");
    }
}
""");

using var parser = new FastParseClient();

Console.WriteLine($"Library : {parser.Version}");
Console.WriteLine($"Path    : {parser.LibraryPath}");

var stats = parser.ParseBytesSummary(source, new ParseOptions
{
    Format = FastParseFormat.Stats
});
Assert(stats.NodeCount > 0, "stats should count nodes");
Assert(stats.OutputLength == 0, "stats should not produce output bytes");

var json = parser.ParseBytes(source, new ParseOptions
{
    Format = FastParseFormat.Json,
    IncludeRules = "method_declaration",
    Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
});
Assert(json.NodeCount == 1, "json should include one method_declaration");
Assert(json.Text.Contains("method_declaration", StringComparison.Ordinal), "json should contain method_declaration");

var binary = parser.ParseBytes(source, new ParseOptions
{
    Format = FastParseFormat.Binary,
    IncludeRules = "method_declaration",
    Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
});
Assert(binary.NodeCount == 1, "binary should include one method_declaration");
Assert(binary.Data.Length > 0, "binary should produce output bytes");
Assert(Encoding.ASCII.GetString(binary.Data).Contains("tsmp-binary", StringComparison.Ordinal), "binary should include schema marker");

var document = FastParseMessagePack.Decode(binary.Data);
Assert(document.Format == "tsmp-binary", "decoded binary should include format marker");
Assert(document.SchemaVersion == 1, "decoded binary should use schema v1");
Assert(document.Nodes[0].Rule == "method_declaration", "decoded binary should include method rule");
Assert(document.Nodes[0].Text is { Length: > 0 }, "decoded binary should keep text bytes");

var summary = parser.ParseBytesSummary(source, new ParseOptions
{
    Format = FastParseFormat.Binary,
    Fields = FastParseField.Rule | FastParseField.ByteRange
});
Assert(summary.NodeCount > 0, "binary summary should count nodes");
Assert(summary.OutputLength > 0, "binary summary should report output length");

try
{
    parser.ParseBytesSummary(source, new ParseOptions
    {
        Language = "missing",
        Format = FastParseFormat.Stats
    });
    throw new InvalidOperationException("invalid language should fail");
}
catch (FastParseException)
{
}

Console.WriteLine($"Stats nodes   : {stats.NodeCount}");
Console.WriteLine($"JSON bytes    : {json.Data.Length}");
Console.WriteLine($"Binary bytes  : {binary.Data.Length}");
Console.WriteLine($"Binary rule   : {document.Nodes[0].Rule}");
Console.WriteLine($"Summary bytes : {summary.OutputLength}");
Console.WriteLine("C# smoke OK");
