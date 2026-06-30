# FastParse .NET Java Quickstart For AI Agents

This guide is intended for an AI coding agent that needs to integrate FastParse into a .NET/C# project and parse Java source code.

## What FastParse Does

FastParse is a native Tree-sitter based parsing library with language bindings. The .NET package exposes a C# API over the native FastParse ABI.

The expected integration model is:

- The parent .NET application owns file IO, queues, databases, and orchestration.
- The parent application passes source code to FastParse in memory as text or bytes.
- FastParse parses the source in RAM and returns output in RAM.
- FastParse should not be treated as a file crawler, database creator, or project scanner.

The base `FastParser` NuGet package includes Java support by default.

## Install From NuGet

From an existing .NET project directory:

```bash
dotnet add package FastParser --version 0.1.0-preview.23
```

For a brand-new console test project:

```bash
dotnet new console -n FastParseJavaDemo
cd FastParseJavaDemo
dotnet add package FastParser --version 0.1.0-preview.23
```

This installs:

- The C# binding.
- The native FastParse library for the current platform.
- Java grammar support by default.
- JSON, CSV, binary MessagePack, stats, and diagnostics output modes.
- Safe native memory release from managed C#.
- Automatic native library loading from the NuGet package layout.

No extra language extension is required for Java.

## Minimal Java AST Example

Use this in `Program.cs`:

```csharp
using FastParse;

var source = """
public class Demo {
    public static void main(String[] args) {
        System.out.println("Hola FastParse");
    }
}
""";

using var parser = new FastParseClient();

var result = parser.ParseText(
    source,
    new ParseOptions
    {
        Language = "java",
        Format = FastParseFormat.Json
    });

Console.WriteLine($"FastParse version: {parser.Version}");
Console.WriteLine($"Native library: {parser.LibraryPath}");
Console.WriteLine($"Node count: {result.NodeCount}");
Console.WriteLine(result.Text);
```

Run it:

```bash
dotnet run
```

By default, when no rule filter or field filter is provided, FastParse is intended to return the full exploratory AST output for Java.

## Parse From Bytes

If the parent application already has bytes, use `ParseBytes`:

```csharp
using FastParse;
using System.Text;

var sourceBytes = Encoding.UTF8.GetBytes("class Demo { void run() {} }");

using var parser = new FastParseClient();

var result = parser.ParseBytes(
    sourceBytes,
    new ParseOptions
    {
        Language = "java",
        Format = FastParseFormat.Json
    });

Console.WriteLine(result.Text);
```

## Select Only Some Java Rules

When the developer already knows which Tree-sitter rules are needed, use `IncludeRules` to reduce output size and processing cost.

```csharp
using FastParse;

var source = """
class Demo {
    void run() {
        System.out.println("fast");
    }
}
""";

using var parser = new FastParseClient();

var result = parser.ParseText(
    source,
    new ParseOptions
    {
        Language = "java",
        Format = FastParseFormat.Json,
        IncludeRules = "class_declaration|method_declaration"
    });

Console.WriteLine(result.Text);
```

## Select Output Fields

Use field flags when the consumer does not need every field. This is useful for production pipelines that only need specific data.

```csharp
using FastParse;

using var parser = new FastParseClient();

var result = parser.ParseText(
    "class Demo { void run() {} }",
    new ParseOptions
    {
        Language = "java",
        Format = FastParseFormat.Json,
        IncludeRules = "method_declaration",
        Fields = FastParseField.Rule |
                 FastParseField.Text |
                 FastParseField.ByteRange |
                 FastParseField.PointRange
    });

Console.WriteLine(result.Text);
```

Important fields for source analysis usually include:

- `Rule`: Tree-sitter grammar rule name.
- `Text`: original source slice for the node.
- `ByteRange`: byte offsets in the original input.
- `PointRange`: line and column positions.

## Binary Output

For high-performance consumers, request binary output instead of JSON text.

```csharp
using FastParse;

using var parser = new FastParseClient();

var result = parser.ParseText(
    "class Demo { void run() {} }",
    new ParseOptions
    {
        Language = "java",
        Format = FastParseFormat.Binary
    });

byte[] payload = result.Data;
Console.WriteLine($"Binary bytes: {payload.Length}");
```

Binary output is not JSON encoded as text. It is intended for consumers that want to decode into native data structures with less string overhead.

## Diagnostics Output

Use diagnostics when the goal is parse quality rather than full AST extraction.

```csharp
using FastParse;

using var parser = new FastParseClient();

var result = parser.ParseText(
    "class Demo {",
    new ParseOptions
    {
        Language = "java",
        Format = FastParseFormat.Diagnostics
    });

Console.WriteLine(result.Text);
```

Diagnostics should be treated as parse-quality information. Native failures are different from parse recovery. Tree-sitter can recover and report syntax problems through `ERROR`, `MISSING`, or `has_error` style diagnostics.

## Concurrency Contract

Recommended conservative model:

- Use one `FastParseClient` per worker thread.
- Load language extensions before starting concurrent workers.
- Keep file reading and database writing outside FastParse.
- Use queues or channels in the parent application.
- Pass source text or bytes into FastParse in RAM.
- Dispose each `FastParseClient` when the worker is done.

FastParse parse calls are designed to be RAM-only calls. The parent .NET process controls thread pools, batching, IO, persistence, and retries.

## Language Extensions

Java is available from the base package:

```bash
dotnet add package FastParser --version 0.1.0-preview.23
```

Other languages are distributed as optional packages. For example, Python:

```bash
dotnet add package FastParser.Language.Python --version 0.1.0-preview.23
```

Then load it before parsing Python:

```csharp
using FastParse;

using var parser = new FastParseClient();
parser.LoadBundledLanguage("python");

var result = parser.ParseText(
    "def hello():\n    print('hi')\n",
    new ParseOptions
    {
        Language = "python",
        Format = FastParseFormat.Json
    });

Console.WriteLine(result.Text);
```

Do not install `FastParser.Language.Python` when only Java parsing is needed.

## Integration Checklist

For an AI agent integrating FastParse into a .NET project:

1. Confirm the project targets a supported .NET version.
2. Install `FastParser` from NuGet.
3. Do not manually copy native libraries for normal NuGet use.
4. Read source files in the parent app if file parsing is needed.
5. Pass source text or bytes to `ParseText` or `ParseBytes`.
6. Start with full JSON AST for exploration.
7. Once needed rules are known, use `IncludeRules`.
8. Once needed fields are known, use `FastParseField` flags.
9. For high-performance pipelines, evaluate `FastParseFormat.Binary`.
10. For parse-quality checks, use diagnostics.
11. Use one parser client per worker thread in concurrent pipelines.

## Key Mental Model

```text
FastParser = native FastParse engine + C# binding + Java by default
FastParser.Language.<Name> = optional language extension package
Parent app = file IO + queues + database writes + orchestration
FastParse = parse source in RAM and return AST/diagnostics/stats in RAM
```
