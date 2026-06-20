# AI Agent Integration Guide

This guide is written for coding agents that need to integrate FastParse into an application.

## First Decision

Do not make FastParse read files or write databases.

Correct architecture:

```text
parent app reads source bytes
parent app calls FastParse
FastParse returns AST data in memory
parent app maps output into objects, files, or databases
```

## Preferred Contract

For production integrations, prefer:

```text
format = binary
include_rules = exact grammar rules needed
fields = exact fields needed
```

Do not request all rules and all fields unless the user is exploring the AST.

## Python Integration

Use the Python binding:

```python
from fastparse import FastParse

parser = FastParse()

source = java_path.read_bytes()
result = parser.parse_bytes(
    source,
    language="java",
    output_format="binary",
    include_rules=["class_declaration", "method_declaration"],
    fields=["id", "parent_id", "rule", "text", "byte_range"],
)

payload = result.data
node_count = result.node_count
```

If JSON is requested:

```python
result = parser.parse_bytes(
    source,
    language="java",
    output_format="json",
    include_rules=["method_declaration"],
    fields=["rule", "text", "range"],
)

document = result.json()
```

## C# Integration

Use the C# binding:

```csharp
using FastParse;

using var parser = new FastParseClient();

var source = File.ReadAllBytes(path);
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
```

For JSON:

```csharp
var result = parser.ParseBytes(source, new ParseOptions
{
    Format = FastParseFormat.Json,
    IncludeRules = "method_declaration",
    Fields = FastParseField.Rule | FastParseField.Text | FastParseField.Range
});

var json = result.Text;
```

## Rule Selection Pattern

If the user asks for Java classes and methods, start with:

```text
class_declaration
interface_declaration
enum_declaration
record_declaration
method_declaration
constructor_declaration
field_declaration
import_declaration
package_declaration
```

If a rule is not available in the grammar, FastParse simply returns zero matches for it.

## Field Selection Pattern

Use this field set for most object extraction:

```text
id
parent_id
rule
text
byte_range
range
```

Add only when needed:

```text
child_count
children
```

Avoid `children` for very large scans unless the user explicitly needs direct child summaries.

## Performance Rules

Fast:

```text
stats + selected rules
binary + selected rules + selected fields
```

Slower:

```text
json + all rules + all fields
binary + all rules + all fields + full database expansion
```

Very expensive:

```text
materializing every AST node text into SQL rows
```

## Error Handling

If a native call fails:

- Surface the native status code.
- Surface `error_message` when available.
- Always free the native result.

Do not swallow unsupported language or invalid argument errors.

## Things Agents Should Not Do

Do not:

- Add file-reading APIs to the C core.
- Add SQLite or database code to the C core.
- Make the C core spawn threads.
- Decode binary output as UTF-8 text.
- Treat `text` in MessagePack as a string.
- Assume all source files are UTF-8.
- Commit generated SQLite databases or native build outputs.

## Recommended Generated App Shape

For a production parent application:

```text
src/
  FastParse adapter
  Domain extraction objects
  Persistence/indexing layer

config/
  selected rules
  selected fields

tests/
  fixture Java source
  expected extracted objects
```

The adapter should be thin. Domain modeling belongs in the parent app, not in FastParse.
