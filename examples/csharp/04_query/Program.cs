using FastParse;

var source = """
public class Demo {
    public void run() {
        System.out.println("query");
    }
}
""";

var query = """
(method_declaration
  name: (identifier) @method.name) @method
""";

using var parser = new FastParseClient();

var result = parser.QueryText(
    source,
    query,
    new QueryOptions
    {
        Language = "java",
        Format = FastParseFormat.Json,
        Fields = FastParseField.CaptureName |
                 FastParseField.Rule |
                 FastParseField.Text |
                 FastParseField.Range |
                 FastParseField.ByteRange
    });

Console.WriteLine($"Captures: {result.NodeCount}");
Console.WriteLine(result.Text);
