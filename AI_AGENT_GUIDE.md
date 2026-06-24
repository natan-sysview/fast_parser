# FastParser AI Agent Guide

Use this guide when an AI agent needs to integrate FastParser into a .NET application.

## Install

```bash
dotnet add package FastParser --version 0.1.0-preview.12
```

Package ID:

```text
FastParser
```

C# namespace:

```csharp
using FastParse;
```

## Default Behavior

`new FastParseClient().ParseText(source)` returns the full Java AST as JSON with the default field set.

FastParser is memory-first:

- Parent applications read source files.
- FastParser receives `string`, `byte[]`, or `ReadOnlySpan<byte>`.
- FastParser returns managed bytes/string data.
- FastParser does not create databases or write source files.

## Common C# Pattern

```csharp
using FastParse;

using var parser = new FastParseClient();

var result = parser.ParseText(javaSource, new ParseOptions
{
    Format = FastParseFormat.Json,
    IncludeRules = "class_declaration|method_declaration",
    Fields = FastParseField.Rule |
             FastParseField.Text |
             FastParseField.ByteRange |
             FastParseField.Range
});

Console.WriteLine(result.NodeCount);
Console.WriteLine(result.Text);
```

## Output Formats

Use:

```text
FastParseFormat.Json    human-readable AST data
FastParseFormat.Csv     flat rows for tabular pipelines
FastParseFormat.Binary  MessagePack for high-throughput consumers
FastParseFormat.Stats   counts only, no output copy
FastParseFormat.Diagnostics small grammar-quality JSON without AST nodes
```

## Field Selection

Default exploration should request all useful fields. Production pipelines should select only what they need.

Common field flags:

```text
FastParseField.Rule
FastParseField.Text
FastParseField.Range
FastParseField.ByteRange
FastParseField.Children
FastParseField.Diagnostics
```

## Rule Selection

Use `IncludeRules` to reduce output:

```csharp
IncludeRules = "class_declaration|method_declaration"
```

Leave it empty to include the full AST.

## Source Normalization

Use the default `FastParseNormalization.AutoSafe` unless the user explicitly needs byte-for-byte original parsing.

For COBOL, `AutoSafe` removes known legacy trailer bytes in RAM before parsing, such as final `0x1A`, `0x7F`, NUL, `FHA`, or a lone final `*` record. Modern languages are left unchanged.

Disable cleanup only when original byte offsets must refer to the unmodified source:

```csharp
Normalization = FastParseNormalization.None
```

## Parse Diagnostics

When code may contain unsupported, incomplete, or newer syntax, request diagnostics:

```csharp
Fields = FastParseField.Rule |
         FastParseField.ByteRange |
         FastParseField.Diagnostics
```

Diagnostics expose Tree-sitter recovery data:

```text
document.HasErrors
document.ErrorNodeCount
node.IsError
node.IsMissing
node.HasError
```

Do not treat `HasErrors = true` as a native exception. Store it as parse quality metadata and decide in the parent application whether to reject, retry, or continue.

## Binary Decoding

```csharp
var result = parser.ParseText(source, new ParseOptions
{
    Format = FastParseFormat.Binary,
    IncludeRules = "method_declaration",
    Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
});

var document = FastParseMessagePack.Decode(result.Data);
Console.WriteLine(document.Nodes[0].Rule);
```

## Native Loading

Normal NuGet use needs no native path configuration. The package includes native libraries for:

```text
linux-x64
osx-arm64
osx-x64
win-x64
```

For advanced manual loading:

```csharp
using var parser = new FastParseClient("/path/to/libfastparse.dylib");
```

or:

```bash
FASTPARSE_LIBRARY_PATH=/path/to/libfastparse.dylib
```

## Threading

Use one `FastParseClient` per worker thread. Keep file IO, queues, and database writes in the parent application.

## Optional Parse Languages

FastParser currently includes Java by default. Future parse languages should be installed as separate language extension packages.

Current preview builds can also load an explicit native extension path:

```csharp
using var parser = new FastParseClient();
parser.LoadLanguageExtension("/path/to/libfastparse_language_cobol.dylib");
```

After loading, set:

```csharp
Language = "cobol"
```

Load extensions before starting concurrent parse workers.

Expected package-manager patterns:

```bash
dotnet add package FastParser.Language.Cobol
pip install fastparse-language-cobol
cargo add fastparse-language-cobol
```

After installing an extension, bindings should load it through a bundled-language API such as:

```text
load_bundled_language("cobol")
```

Read `docs/language_extensions.md` before generating code for optional parse languages.

## Avoid

- Do not parse by shelling out to a CLI when using the binding.
- Do not write temporary source files just to parse them.
- Do not request the full AST in production if only a few rules/fields are needed.
- Do not assume binary output is UTF-8 text; decode it as MessagePack.

## High-Value Docs In This Package

```text
docs/contracts.md
docs/language_extensions.md
docs/output_formats.md
docs/binary_schema.md
docs/csharp_binding.md
docs/encoding.md
docs/platforms.md
docs/versioning.md
examples/csharp/01_parse_string/
examples/csharp/02_binary_decode/
examples/csharp/nuget/01_parse_string/
examples/csharp/nuget/02_binary_decode/
```
