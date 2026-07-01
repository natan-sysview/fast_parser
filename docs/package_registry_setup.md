# Package Registry Setup

This document lists the external registry configuration required before a tagged release can publish FastParse packages.

FastParse uses GitHub Actions and registry trusted publishing whenever possible. The repository should not store long-lived API tokens unless a registry has no OIDC option.

## GitHub Repository Variables

Configure these variables under:

```text
GitHub repository -> Settings -> Secrets and variables -> Actions -> Variables
```

| Variable | Value | Effect |
|---|---|---|
| `PYPI_PUBLISH` | `true` | Publish the core `fastparse` wheels to PyPI. |
| `PYPI_LANGUAGE_PYTHON_PUBLISH` | `true` | Publish `fastparse-language-python` wheels to PyPI. |
| `PYPI_LANGUAGE_JAVA_FRAMEWORKS_PUBLISH` | `true` | Publish `fastparse-language-java-frameworks` wheels to PyPI. |
| `PYPI_LANGUAGE_JAVASWING_PUBLISH` | `true` | Publish `fastparse-language-javaswing` wheels to PyPI. |
| `NUGET_LANGUAGE_PYTHON_PUBLISH` | `true` | Publish `FastParser.Language.Python` to nuget.org. |
| `NUGET_LANGUAGE_JAVA_FRAMEWORKS_PUBLISH` | `true` | Publish `FastParser.Language.JavaFrameworks` to nuget.org. |
| `NUGET_LANGUAGE_JAVASWING_PUBLISH` | `true` | Publish `FastParser.Language.JavaSwing` to nuget.org. |

The core `FastParser` NuGet package is published on tags by the existing NuGet trusted publishing step.

## PyPI Trusted Publishers

PyPI needs one trusted publisher per PyPI project name.

Core package:

```text
Project name : fastparse
Publisher    : GitHub
Owner        : natan-sysview
Repository   : fast_parser
Workflow     : release.yml
Environment  : any / blank
```

Python language extension:

```text
Project name : fastparse-language-python
Publisher    : GitHub
Owner        : natan-sysview
Repository   : fast_parser
Workflow     : release.yml
Environment  : any / blank
```

Future Rust language extension:

```text
Project name : fastparse-language-rust
Publisher    : GitHub
Owner        : natan-sysview
Repository   : fast_parser
Workflow     : release.yml
Environment  : any / blank
```

Important: a pending publisher does not reserve the package name. The first tagged publish creates the project if nobody else has claimed it.

Java Frameworks language extension:

```text
Project name : fastparse-language-java-frameworks
Publisher    : GitHub
Owner        : natan-sysview
Repository   : fast_parser
Workflow     : release.yml
Environment  : any / blank
```

JavaSwing language extension:

```text
Project name : fastparse-language-javaswing
Publisher    : GitHub
Owner        : natan-sysview
Repository   : fast_parser
Workflow     : publish-javaswing-pypi.yml
Environment  : any / blank
```

`release.yml` can also be extended for future combined releases. Use `publish-javaswing-pypi.yml` when publishing only the JavaSwing PyPI extension against an already published FastParse core version.

## NuGet Trusted Publishing

NuGet needs a trusted publishing policy for each NuGet package ID.

Core package:

```text
Package ID       : FastParser
Repository owner : natan-sysview
Repository       : fast_parser
Workflow file    : release.yml
Environment      : any / blank
```

Python language extension:

```text
Package ID       : FastParser.Language.Python
Repository owner : natan-sysview
Repository       : fast_parser
Workflow file    : release.yml
Environment      : any / blank
```

Future Rust language extension:

```text
Package ID       : FastParser.Language.Rust
Repository owner : natan-sysview
Repository       : fast_parser
Workflow file    : release.yml
    Environment      : any / blank
```

Java Frameworks language extension:

```text
Package ID       : FastParser.Language.JavaFrameworks
Repository owner : natan-sysview
Repository       : fast_parser
Workflow file    : release.yml
Environment      : any / blank
```

JavaSwing language extension:

```text
Package ID       : FastParser.Language.JavaSwing
Repository owner : natan-sysview
Repository       : fast_parser
Workflow file    : publish-javaswing-nuget.yml
Environment      : any / blank
```

`release.yml` also supports JavaSwing for future tagged releases. Use `publish-javaswing-nuget.yml` when publishing only the JavaSwing NuGet extension against an already published FastParser core version.

## Release Flow

After the registry setup is complete:

```bash
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions will:

1. Build native core archives for Linux, macOS arm64, macOS x64, and Windows.
2. Build core NuGet and PyPI packages.
3. Build Python, Java Frameworks, and JavaSwing language extension native archives.
4. Build `fastparse-language-python` wheels.
5. Build `fastparse-language-java-frameworks` wheels.
6. Build `FastParser.Language.Python`.
7. Build `FastParser.Language.JavaFrameworks`.
8. Build `FastParser.Language.JavaSwing`.
9. Publish enabled packages to their registries.
10. Run post-publish smoke tests from the public registries.
11. Attach release assets and `SHA256SUMS.txt` to GitHub Releases.

## Developer Install Commands

Python:

```bash
pip install fastparse fastparse-language-python
pip install fastparse fastparse-language-java-frameworks
pip install fastparse fastparse-language-javaswing
```

C#:

```bash
dotnet add package FastParser
dotnet add package FastParser.Language.Python
dotnet add package FastParser.Language.JavaFrameworks
dotnet add package FastParser.Language.JavaSwing
```

Minimal Python smoke:

```python
from fastparse import FastParse

parser = FastParse()
parser.load_bundled_language("python")
result = parser.parse_text("def hello(): pass", language="python")
print(result.node_count)
```

Minimal Python Java Frameworks smoke:

```python
from fastparse import FastParse
import fastparse_language_java_frameworks as java_frameworks

parser = FastParse()
parser.load_bundled_language("java-frameworks")
query = java_frameworks.query_path("frameworks").read_text()
result = parser.query_text_summary(
    "import org.springframework.stereotype.Service;\n@Service class Demo {}\n",
    query,
    language="java-frameworks",
    output_format="stats",
    fields=["capture_name"],
)
print(result.node_count)
```

Minimal C# smoke:

```csharp
using FastParse;

using var parser = new FastParseClient();
parser.LoadBundledLanguage("python");
var result = parser.ParseText("def hello(): pass", new ParseOptions { Language = "python" });
Console.WriteLine(result.NodeCount);
```

Minimal C# JavaSwing smoke:

```csharp
using FastParse;

using var parser = new FastParseClient();
parser.LoadBundledLanguage("javaswing");
var result = parser.ParseText(
    "import javax.swing.*; class Demo extends JFrame { JButton b = new JButton(\"OK\"); }",
    new ParseOptions { Language = "javaswing" });
Console.WriteLine(result.NodeCount);
```

Minimal C# Java Frameworks smoke:

```csharp
using FastParse;

using var parser = new FastParseClient();
parser.LoadBundledLanguage("java-frameworks");
var result = parser.ParseText(
    "import org.springframework.stereotype.Service;\n@Service class Demo {}\n",
    new ParseOptions { Language = "java-frameworks" });
Console.WriteLine(result.NodeCount);
```
