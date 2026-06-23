using System.Text;
using FastParse;
using Xunit;

namespace FastParse.Tests;

public sealed class FastParseClientTests
{
    private const string Source = "class Demo { void run() { System.out.println(\"test\"); } }";

    [Fact]
    public void ParseTextDefaultReturnsFullJsonAst()
    {
        using var parser = new FastParseClient();

        var result = parser.ParseText(Source);

        Assert.Equal(FastParseFormat.Json, result.Format);
        Assert.True(result.NodeCount > 0);
        using var document = result.JsonDocument();
        Assert.Equal("java", document.RootElement.GetProperty("language").GetString());
        Assert.True(document.RootElement.GetProperty("nodes").GetArrayLength() > 0);
        Assert.Contains("class_declaration", result.Text, StringComparison.Ordinal);
    }

    [Fact]
    public void ParseTextFiltersRulesAndFields()
    {
        using var parser = new FastParseClient();

        var result = parser.ParseText(Source, new ParseOptions
        {
            IncludeRules = "method_declaration",
            Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
        });

        Assert.Equal(1UL, result.NodeCount);
        using var document = result.JsonDocument();
        var node = document.RootElement.GetProperty("nodes")[0];
        Assert.Equal("method_declaration", node.GetProperty("rule").GetString());
        Assert.Contains("void run()", node.GetProperty("text").GetString(), StringComparison.Ordinal);
        Assert.True(node.TryGetProperty("startByte", out _));
        Assert.False(node.TryGetProperty("startLine", out _));
    }

    [Fact]
    public void CsvOutputHonorsRequestedFields()
    {
        using var parser = new FastParseClient();

        var result = parser.ParseText(Source, new ParseOptions
        {
            Format = FastParseFormat.Csv,
            IncludeRules = "method_declaration",
            Fields = FastParseField.Rule | FastParseField.Text
        });

        Assert.Equal(FastParseFormat.Csv, result.Format);
        Assert.Equal(1UL, result.NodeCount);
        Assert.StartsWith("rule,text", result.Text, StringComparison.Ordinal);
        Assert.Contains("method_declaration", result.Text, StringComparison.Ordinal);
    }

    [Fact]
    public void BinaryOutputDecodesToManagedObjects()
    {
        using var parser = new FastParseClient();

        var result = parser.ParseText(Source, new ParseOptions
        {
            Format = FastParseFormat.Binary,
            IncludeRules = "method_declaration",
            Fields = FastParseField.Rule | FastParseField.Text
        });
        var document = FastParseMessagePack.Decode(result.Data);

        Assert.Equal(FastParseFormat.Binary, result.Format);
        Assert.Equal(1UL, result.NodeCount);
        Assert.Equal("tsmp-binary", document.Format);
        Assert.Equal("java", document.Language);
        Assert.Equal("method_declaration", document.Nodes[0].Rule);
        Assert.Contains("void run()", Encoding.UTF8.GetString(document.Nodes[0].Text!), StringComparison.Ordinal);
    }

    [Fact]
    public void StatsSummaryAvoidsCopyingOutputBytes()
    {
        using var parser = new FastParseClient();

        var summary = parser.ParseTextSummary(Source, new ParseOptions
        {
            Format = FastParseFormat.Stats
        });

        Assert.Equal(FastParseFormat.Stats, summary.Format);
        Assert.True(summary.NodeCount > 0);
        Assert.Equal(0UL, summary.OutputLength);
    }

    [Fact]
    public void ExplicitNativeLibraryPathLoadsSuccessfully()
    {
        var libraryPath = FindNativeLibrary();

        using var parser = new FastParseClient(libraryPath);

        Assert.Equal(libraryPath, parser.LibraryPath);
        Assert.StartsWith("fastparse-c-api/", parser.Version, StringComparison.Ordinal);
    }

    [Fact]
    public void InvalidLanguageThrowsFastParseException()
    {
        using var parser = new FastParseClient();

        var error = Assert.Throws<FastParseException>(() => parser.ParseText(Source, new ParseOptions
        {
            Language = "missing-language"
        }));

        Assert.Contains("language", error.Message, StringComparison.OrdinalIgnoreCase);
    }

    private static string FindNativeLibrary()
    {
        var fileName = OperatingSystem.IsWindows()
            ? "fastparse.dll"
            : OperatingSystem.IsMacOS()
                ? "libfastparse.dylib"
                : "libfastparse.so";

        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var candidate = Path.Combine(directory.FullName, "bin", fileName);
            if (File.Exists(candidate))
            {
                return candidate;
            }

            directory = directory.Parent;
        }

        throw new FileNotFoundException($"Could not find native FastParse library {fileName}.");
    }
}
