using FastParse;

using var parser = new FastParseClient();

var result = parser.ParseText(
    "class Demo { void run() { System.out.println(\"nuget\"); } }",
    new ParseOptions
    {
        Format = FastParseFormat.Json,
        IncludeRules = "method_declaration",
        Fields = FastParseField.Rule |
                 FastParseField.Text |
                 FastParseField.ByteRange
    });

Console.WriteLine($"Version: {parser.Version}");
Console.WriteLine($"Native : {parser.LibraryPath}");
Console.WriteLine($"Nodes  : {result.NodeCount}");
Console.WriteLine(result.Text);
