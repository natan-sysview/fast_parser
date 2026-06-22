# FastParser for .NET

FastParser is a thin C# binding over the FastParse native C ABI.

It parses source bytes in memory and returns AST data as JSON, CSV, binary MessagePack, or stats. The current native package includes the Java Tree-sitter grammar.

## Install

```bash
dotnet add package FastParser --version 0.1.0-preview.1
```

The package includes RID-specific native libraries:

```text
runtimes/linux-x64/native/libfastparse.so
runtimes/osx-arm64/native/libfastparse.dylib
runtimes/osx-x64/native/libfastparse.dylib
runtimes/win-x64/native/fastparse.dll
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
        Fields = FastParseField.Rule |
                 FastParseField.Text |
                 FastParseField.ByteRange
    });

Console.WriteLine(result.NodeCount);
Console.WriteLine(result.Text);
```

## Binary Output

For `FastParseFormat.Binary`, `ParseResult.Data` contains MessagePack bytes. The package includes a small schema-specific decoder:

```csharp
var binary = parser.ParseText(source, new ParseOptions
{
    Format = FastParseFormat.Binary,
    IncludeRules = "method_declaration",
    Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
});

var document = FastParseMessagePack.Decode(binary.Data);
Console.WriteLine(document.SchemaVersion);
Console.WriteLine(document.Nodes[0].Rule);
```

## Stats Without Output Copy

```csharp
var summary = parser.ParseTextSummary(source, new ParseOptions
{
    Format = FastParseFormat.Stats
});

Console.WriteLine(summary.NodeCount);
Console.WriteLine(summary.OutputLength); // 0 for stats
```

## Native Library Loading

Normal NuGet use does not require `FASTPARSE_LIBRARY_PATH`; .NET resolves the bundled native asset for the current RID.

For advanced/manual loading, pass a path explicitly:

```csharp
using var parser = new FastParseClient("/path/to/libfastparse.dylib");
```

Or set:

```bash
FASTPARSE_LIBRARY_PATH=/path/to/libfastparse.dylib
```

## Threading

Use one `FastParseClient` per worker thread for simple high-throughput code. Parent applications still own thread pools, queues, and database coordination.

## Package Name vs Namespace

The public NuGet package ID is `FastParser`.

The C# namespace is `FastParse`:

```csharp
using FastParse;
```
