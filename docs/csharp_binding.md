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

## NuGet Use

The release workflow builds a local/package artifact:

```text
FastParser.<version>.nupkg
FastParser.<version>.snupkg
```

Install it from a local package directory:

```bash
dotnet add package FastParser --version 0.1.0-preview.11 --source /path/to/package-dir
```

Once the package is published to nuget.org, the command becomes:

```bash
dotnet add package FastParser
```

The NuGet package carries native libraries using standard RID folders:

```text
AI_AGENT_GUIDE.md
docs/
examples/csharp/01_parse_string/
examples/csharp/02_binary_decode/
examples/csharp/nuget/01_parse_string/
examples/csharp/nuget/02_binary_decode/
lib/net8.0/FastParse.dll
lib/net8.0/FastParse.pdb
lib/net8.0/FastParse.xml
lib/net9.0/FastParse.dll
lib/net9.0/FastParse.pdb
lib/net9.0/FastParse.xml
runtimes/linux-x64/native/libfastparse.so
runtimes/osx-arm64/native/libfastparse.dylib
runtimes/osx-x64/native/libfastparse.dylib
runtimes/win-x64/native/fastparse.dll
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
             FastParseField.Diagnostics |
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

## Parse Diagnostics

Use diagnostics when the parent application needs to know whether Tree-sitter recovered from invalid or unsupported syntax:

```csharp
var result = parser.ParseBytes(source, new ParseOptions
{
    Language = "java",
    Format = FastParseFormat.Binary,
    Fields = FastParseField.Rule |
             FastParseField.ByteRange |
             FastParseField.Diagnostics
});

var document = FastParseMessagePack.Decode(result.Data);
Console.WriteLine(document.HasErrors);
Console.WriteLine(document.ErrorNodeCount);
Console.WriteLine(document.Nodes[0].HasError);
```

`HasErrors = true` is not a native failure. It means parsing succeeded but the grammar reported `ERROR` or `MISSING` nodes.

## Diagnostics Format

Use `FastParseFormat.Diagnostics` for large grammar-quality scans where the AST is not needed:

```csharp
var result = parser.ParseBytes(source, new ParseOptions
{
    Language = "cobol",
    Format = FastParseFormat.Diagnostics
});

using var document = result.JsonDocument();
Console.WriteLine(document.RootElement.GetProperty("hasErrors").GetBoolean());
Console.WriteLine(document.RootElement.GetProperty("errorNodeCount").GetUInt64());
```

This format returns a small JSON payload and does not include a `nodes` array.

## Library Loading

The binding searches upward from `AppContext.BaseDirectory` for:

```text
libfastparse.dylib
libfastparse.so
fastparse.dll
bin/libfastparse.dylib
bin/libfastparse.so
bin/fastparse.dll
```

If the native library is supplied by NuGet, the binding also allows .NET's native library resolution to load the RID-specific asset.

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
FastParseClient.LoadLanguageExtension(...)
FastParseClient.LanguageAvailable(...)
ParseOptions
ParseResult
ParseSummary
FastParseMessagePack.Decode(...)
```

## Threading

Use one `FastParseClient` per worker thread for simple high-throughput code.

The native parser is thread-safe per call. Parent applications still own thread pools and SQLite/database coordination.

## Language Extensions

Load optional parse languages from a native extension path before parsing:

```csharp
using var parser = new FastParseClient();

var load = parser.LoadLanguageExtension("/path/to/libfastparse_language_cobol.dylib");
Console.WriteLine(load.Language);     // cobol
Console.WriteLine(load.DisplayName);  // COBOL

var result = parser.ParseText(cobolSource, new ParseOptions
{
    Language = "cobol",
    Format = FastParseFormat.Json,
    Fields = FastParseField.Rule | FastParseField.Diagnostics
});
```

Load extensions before starting concurrent parse workers.

## Source Normalization

`ParseOptions.Normalization` controls memory-only cleanup before parsing:

```csharp
var result = parser.ParseBytes(cobolSourceBytes, new ParseOptions
{
    Language = "cobol",
    Format = FastParseFormat.Binary,
    Normalization = FastParseNormalization.AutoSafe
});
```

Modes:

```text
FastParseNormalization.AutoSafe
FastParseNormalization.None
FastParseNormalization.CobolFixedLegacy
```

`AutoSafe` is the default. For COBOL it removes known fixed-format legacy trailer bytes such as final `0x1A`, `0x7F`, NUL, `FHA`, or a lone final `*` record. Modern languages are left unchanged.

Use `None` when the caller needs byte-for-byte parsing with no cleanup.

## Debugging And Symbols

The NuGet package is built with portable PDBs and SourceLink. The release workflow also publishes a `.snupkg` symbols package to nuget.org, so IDEs/debuggers can map package code back to the exact GitHub source revision.
