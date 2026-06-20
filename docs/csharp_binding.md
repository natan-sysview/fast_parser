# C# Binding

The C# binding uses P/Invoke over the FastParse C ABI.

Path:

```text
bindings/csharp/FastParse
```

## Local Use From Checkout

```bash
dotnet run --project examples/csharp/01_parse_string/FastParse.ParseStringExample.csproj
```

## Basic Use

```csharp
using FastParse;

using var parser = new FastParseClient();

var source = File.ReadAllBytes("Demo.java");
var result = parser.ParseBytes(source, new ParseOptions
{
    Language = "java",
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

```csharp
var result = parser.ParseBytes(source, new ParseOptions
{
    Language = "java",
    Format = FastParseFormat.Binary,
    IncludeRules = "class_declaration|method_declaration",
    Fields = FastParseField.Id |
             FastParseField.ParentId |
             FastParseField.Rule |
             FastParseField.Text |
             FastParseField.ByteRange
});

byte[] payload = result.Data;
```

The binding includes a small schema-specific decoder:

```csharp
var document = FastParseMessagePack.Decode(payload);
Console.WriteLine(document.SchemaVersion);
Console.WriteLine(document.Nodes[0].Rule);
```

For production, applications may also decode MessagePack with a dedicated package such as MessagePack-CSharp.

## Library Loading

The binding searches upward from `AppContext.BaseDirectory` for:

```text
bin/libfastparse.dylib
bin/libfastparse.so
bin/fastparse.dll
```

Override explicitly:

```bash
FASTPARSE_LIBRARY_PATH=/path/to/libfastparse.dylib dotnet run --project your.csproj
```

Compatibility:

```bash
TSMP_LIBRARY_PATH=/path/to/libfastparse.dylib dotnet run --project your.csproj
```

## API Surface

```text
FastParseClient
FastParseClient.Version
FastParseClient.ParseBytes(...)
FastParseClient.ParseText(...)
FastParseClient.ParseBytesSummary(...)
ParseOptions
ParseResult
ParseSummary
FastParseMessagePack.Decode(...)
```

## Threading

Use one `FastParseClient` per worker thread for simple high-throughput code.

The native parser is thread-safe per call. Parent applications still own thread pools and SQLite/database coordination.
