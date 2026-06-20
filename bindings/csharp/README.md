# FastParse C# Binding

Thin C# binding over the FastParse C ABI.

Current status:

- Loads `libfastparse.dylib`, `libfastparse.so`, or `fastparse.dll`.
- Prefers `fastparse_*` native symbols.
- Falls back to `tsmp_*` compatibility symbols.
- Supports JSON, CSV, Binary MessagePack, and Stats.
- Copies native output into managed `byte[]`.
- Always releases native memory through `fastparse_result_free`.

## Example

From the lab root:

```bash
./compila_lib.sh
dotnet run --project examples/csharp/01_parse_string/FastParse.ParseStringExample.csproj
```

Override native library path:

```bash
FASTPARSE_LIBRARY_PATH=/path/to/libfastparse.dylib \
dotnet run --project examples/csharp/01_parse_string/FastParse.ParseStringExample.csproj
```

## Basic Use

```csharp
using FastParse;

using var parser = new FastParseClient();

var result = parser.ParseText(
    "class Demo { void run() {} }",
    new ParseOptions
    {
        Format = FastParseFormat.Json,
        IncludeRules = "method_declaration",
        Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
    });

Console.WriteLine(result.NodeCount);
Console.WriteLine(result.Text);
```

## Binary

For `FastParseFormat.Binary`, `ParseResult.Data` contains MessagePack bytes.

This binding includes a small schema-specific decoder:

```csharp
var document = FastParseMessagePack.Decode(result.Data);

Console.WriteLine(document.SchemaVersion);
Console.WriteLine(document.Nodes[0].Rule);
Console.WriteLine(document.Nodes[0].Text); // byte[]
```

It intentionally does not depend on MessagePack-CSharp. A future optional package can add MessagePack-CSharp support for broader MessagePack tooling.

Larger runnable applications live under `examples/csharp/`; the binding folder intentionally contains only reusable C# binding code.
