using FastParse;

var source = """
public class Demo {
    public void run(String name) {
        System.out.println(name);
    }
}
""";

using var parser = new FastParseClient();

var result = parser.ParseText(source, new ParseOptions
{
    Format = FastParseFormat.Binary,
    IncludeRules = "method_declaration",
    Fields = FastParseField.Rule |
             FastParseField.Text |
             FastParseField.ByteRange
});

var document = FastParseMessagePack.Decode(result.Data);

if (document.Nodes.Count != 1)
{
    throw new InvalidOperationException("Expected one method_declaration node.");
}

var node = document.Nodes[0];
Console.WriteLine($"Format : {document.Format}");
Console.WriteLine($"Schema : {document.SchemaVersion}");
Console.WriteLine($"Rule   : {node.Rule}");
Console.WriteLine($"Bytes  : {result.Data.Length}");
Console.WriteLine("OK");
