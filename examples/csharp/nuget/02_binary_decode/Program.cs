using FastParse;

using var parser = new FastParseClient();

var result = parser.ParseText(
    "class Demo { void run() { System.out.println(\"binary\"); } }",
    new ParseOptions
    {
        Format = FastParseFormat.Binary,
        IncludeRules = "method_declaration",
        Fields = FastParseField.Rule |
                 FastParseField.Text |
                 FastParseField.ByteRange
    });

var document = FastParseMessagePack.Decode(result.Data);
var method = document.Nodes.Single();

Console.WriteLine($"Format: {document.Format}");
Console.WriteLine($"Schema: {document.SchemaVersion}");
Console.WriteLine($"Rule  : {method.Rule}");
Console.WriteLine($"Bytes : {result.Data.Length}");
