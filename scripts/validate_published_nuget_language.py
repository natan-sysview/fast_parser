#!/usr/bin/env python3
"""Validate a published FastParser language extension package from nuget.org."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


CORE_PACKAGE = "FastParser"
SOURCE = "https://api.nuget.org/v3/index.json"
CORE_INDEX_URL = "https://api.nuget.org/v3-flatcontainer/fastparser/index.json"

PYTHON_PROGRAM = r'''using FastParse;

using var parser = new FastParseClient();

var load = parser.LoadBundledLanguage("python");
if (load.Language != "python" || !parser.LanguageAvailable("python"))
{
    throw new InvalidOperationException("published language NuGet load smoke failed");
}

var json = parser.ParseText(
    "def hello(name):\n    return name\n",
    new ParseOptions
    {
        Language = "python",
        Format = FastParseFormat.Json,
        IncludeRules = "function_definition",
        Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
    });

if (json.NodeCount != 1 || !json.Text.Contains("function_definition", StringComparison.Ordinal))
{
    throw new InvalidOperationException("published language NuGet JSON smoke failed");
}

var diagnostics = parser.ParseText(
    "def broken(\n",
    new ParseOptions
    {
        Language = "python",
        Format = FastParseFormat.Diagnostics
    });

using var diagnosticsDocument = diagnostics.JsonDocument();
if (diagnosticsDocument.RootElement.TryGetProperty("nodes", out _) ||
    !diagnosticsDocument.RootElement.GetProperty("hasErrors").GetBoolean())
{
    throw new InvalidOperationException("published language NuGet diagnostics smoke failed");
}

Console.WriteLine("FastParser published language NuGet smoke OK");
Console.WriteLine(parser.Version);
Console.WriteLine(parser.LibraryPath);
'''

JAVA_FRAMEWORKS_PROGRAM = r'''using FastParse;

using var parser = new FastParseClient();

var load = parser.LoadBundledLanguage("java-frameworks");
if (load.Language != "java-frameworks" || !parser.LanguageAvailable("java-frameworks"))
{
    throw new InvalidOperationException("published Java Frameworks language NuGet load smoke failed");
}

var source = "import org.springframework.stereotype.Service;\n@Service class Demo { void x(){ org.springframework.jdbc.core.JdbcTemplate t; } }\n";
var json = parser.ParseText(
    source,
    new ParseOptions
    {
        Language = "java-frameworks",
        Format = FastParseFormat.Json,
        Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
    });

if (json.NodeCount == 0 || !json.Text.Contains("program", StringComparison.Ordinal))
{
    throw new InvalidOperationException("published Java Frameworks language NuGet JSON smoke failed");
}

var queryPath = Path.Combine(AppContext.BaseDirectory, "fastparse", "languages", "java-frameworks", "queries", "frameworks.scm");
if (!File.Exists(queryPath))
{
    throw new InvalidOperationException($"Framework query was not copied to output: {queryPath}");
}

var query = File.ReadAllText(queryPath);
var captures = parser.QueryTextSummary(
    source,
    query,
    new QueryOptions
    {
        Language = "java-frameworks",
        Format = FastParseFormat.Stats,
        Fields = FastParseField.CaptureName
    });

if (captures.NodeCount == 0)
{
    throw new InvalidOperationException("published Java Frameworks language NuGet query smoke failed");
}

var diagnostics = parser.ParseText(
    "class Broken {",
    new ParseOptions
    {
        Language = "java-frameworks",
        Format = FastParseFormat.Diagnostics
    });

using var diagnosticsDocument = diagnostics.JsonDocument();
if (!diagnosticsDocument.RootElement.GetProperty("hasErrors").GetBoolean())
{
    throw new InvalidOperationException("published Java Frameworks language NuGet diagnostics smoke failed");
}

Console.WriteLine("FastParser published language NuGet smoke OK");
Console.WriteLine(parser.Version);
Console.WriteLine(parser.LibraryPath);
'''

JAVASWING_PROGRAM = r'''using FastParse;

using var parser = new FastParseClient();

var load = parser.LoadBundledLanguage("javaswing");
if (load.Language != "javaswing" || !parser.LanguageAvailable("javaswing"))
{
    throw new InvalidOperationException("published JavaSwing language NuGet load smoke failed");
}

var source = """
import javax.swing.*;
class Demo extends JFrame {
    JButton button = new JButton("OK");
    void build() {
        JPanel panel = new JPanel();
        panel.add(button);
    }
}
""";

var json = parser.ParseText(
    source,
    new ParseOptions
    {
        Language = "javaswing",
        Format = FastParseFormat.Json,
        IncludeRules = "javaswing_screen|javaswing_component_creation|javaswing_component_field|javaswing_container_add",
        Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
    });

if (json.NodeCount == 0 || !json.Text.Contains("javaswing_", StringComparison.Ordinal))
{
    throw new InvalidOperationException("published JavaSwing language NuGet JSON smoke failed");
}

var queryPath = Path.Combine(AppContext.BaseDirectory, "fastparse", "languages", "javaswing", "queries", "swing.scm");
if (!File.Exists(queryPath))
{
    throw new InvalidOperationException($"Swing query was not copied to output: {queryPath}");
}

var query = File.ReadAllText(queryPath);
var captures = parser.QueryTextSummary(
    source,
    query,
    new QueryOptions
    {
        Language = "javaswing",
        Format = FastParseFormat.Stats,
        Fields = FastParseField.CaptureName
    });

if (captures.NodeCount == 0)
{
    throw new InvalidOperationException("published JavaSwing language NuGet query smoke failed");
}

var diagnostics = parser.ParseText(
    "class Broken {",
    new ParseOptions
    {
        Language = "javaswing",
        Format = FastParseFormat.Diagnostics
    });

using var diagnosticsDocument = diagnostics.JsonDocument();
if (!diagnosticsDocument.RootElement.GetProperty("hasErrors").GetBoolean())
{
    throw new InvalidOperationException("published JavaSwing language NuGet diagnostics smoke failed");
}

Console.WriteLine("FastParser published language NuGet smoke OK");
Console.WriteLine(parser.Version);
Console.WriteLine(parser.LibraryPath);
'''


COBOL_PROGRAM = r'''using System.Text;
using FastParse;

using var parser = new FastParseClient();

var load = parser.LoadBundledLanguage("cobol");
if (load.Language != "cobol" || !parser.LanguageAvailable("cobol"))
{
    throw new InvalidOperationException("FastParser.Language.Cobol load smoke failed");
}

var source = """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-NAME PIC X(10) VALUE 'CARLOS'.
       PROCEDURE DIVISION.
           DISPLAY WS-NAME.
           EXEC SQL
              COMMIT
           END-EXEC.
           GOBACK.
       END PROGRAM HELLO.
""";

var json = parser.ParseText(
    source,
    new ParseOptions
    {
        Language = "cobol",
        Format = FastParseFormat.Json,
        IncludeRules = "program_definition|exec_sql_statement|display_statement",
        Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
    });

if (json.NodeCount == 0 ||
    !json.Text.Contains("program_definition", StringComparison.Ordinal) ||
    !json.Text.Contains("exec_sql_statement", StringComparison.Ordinal))
{
    throw new InvalidOperationException("published COBOL language NuGet JSON smoke failed");
}

var diagnostics = parser.ParseText(
    source,
    new ParseOptions
    {
        Language = "cobol",
        Format = FastParseFormat.Diagnostics
    });

using var diagnosticsDocument = diagnostics.JsonDocument();
if (diagnosticsDocument.RootElement.GetProperty("hasErrors").GetBoolean())
{
    throw new InvalidOperationException("published COBOL language NuGet diagnostics smoke found errors");
}

var ebcdicCopybook = Convert.FromHexString("40404040404040F0F140D9C5C760E3C5D3C1F0F14B0D254040404040404040404040F0F240E2C4E3D4D6E5D4E3D640D7C9C340E74DF1F05D4B0D25");
var ebcdicDiagnostics = parser.ParseBytes(
    ebcdicCopybook,
    new ParseOptions
    {
        Language = "cobol",
        Format = FastParseFormat.Diagnostics,
        Normalization = FastParseNormalization.AutoSafe
    });

using var ebcdicDocument = ebcdicDiagnostics.JsonDocument();
if (ebcdicDocument.RootElement.GetProperty("hasErrors").GetBoolean())
{
    throw new InvalidOperationException("published COBOL language NuGet EBCDIC diagnostics smoke found errors");
}

var tabbedCopybook = Encoding.UTF8.GetBytes("       01 RCX11.\n\t 02 FCX11-CDEMP               PIC 9(02).\n");
var tabbedDiagnostics = parser.ParseBytes(
    tabbedCopybook,
    new ParseOptions
    {
        Language = "cobol",
        Format = FastParseFormat.Diagnostics,
        Normalization = FastParseNormalization.AutoSafe
    });

using var tabbedDocument = tabbedDiagnostics.JsonDocument();
if (tabbedDocument.RootElement.GetProperty("hasErrors").GetBoolean())
{
    throw new InvalidOperationException("published COBOL language NuGet tab-expanded diagnostics smoke found errors");
}

Console.WriteLine("FastParser published language NuGet smoke OK");
Console.WriteLine(parser.Version);
Console.WriteLine(parser.LibraryPath);
'''


def run_command(command: list[str], *, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stdout}")
    return completed


def smoke_framework(env: dict[str, str]) -> str:
    completed = run_command(["dotnet", "--list-sdks"], env=env)
    majors = []
    for line in completed.stdout.splitlines():
        version = line.split()[0] if line.split() else ""
        major = version.split(".", 1)[0]
        if major.isdigit():
            majors.append(int(major))
    if 9 in majors:
        return "net9.0"
    if 10 in majors:
        return "net10.0"
    if 8 in majors:
        return "net8.0"
    return "net9.0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a FastParser.Language.* package from nuget.org.")
    parser.add_argument("--version", required=True)
    parser.add_argument("--core-version", help="FastParser dependency version. Defaults to --version.")
    parser.add_argument("--language", default="python")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--interval-seconds", type=int, default=30)
    return parser.parse_args()


def package_language_name(language: str) -> str:
    if language.strip().lower().replace("-", "_") == "javaswing":
        return "JavaSwing"
    return "".join(part.capitalize() for part in language.replace("-", "_").split("_"))


def package_id(language: str) -> str:
    return f"FastParser.Language.{package_language_name(language)}"


def package_index_url(language: str) -> str:
    return f"https://api.nuget.org/v3-flatcontainer/{package_id(language).lower()}/index.json"


def smoke_program(language: str) -> str:
    if language == "java-frameworks":
        return JAVA_FRAMEWORKS_PROGRAM
    if language == "javaswing":
        return JAVASWING_PROGRAM
    if language == "cobol":
        return COBOL_PROGRAM
    return PYTHON_PROGRAM


def published_versions(index_url: str) -> set[str]:
    try:
        with urllib.request.urlopen(index_url, timeout=20) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return set()
        raise
    return set(payload.get("versions", []))


def wait_for_version(package_id: str, index_url: str, version: str, timeout_seconds: int, interval_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    version = version.lower()
    while True:
        versions = published_versions(index_url)
        if version in versions:
            return
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{package_id} {version} was not indexed by nuget.org")
        print(f"Waiting for {package_id} {version} to be indexed by nuget.org...", flush=True)
        time.sleep(interval_seconds)


def main() -> int:
    args = parse_args()
    core_version = args.core_version or args.version
    language_package = package_id(args.language)
    language_index_url = package_index_url(args.language)
    wait_for_version(CORE_PACKAGE, CORE_INDEX_URL, core_version, args.timeout_seconds, args.interval_seconds)
    wait_for_version(language_package, language_index_url, args.version, args.timeout_seconds, args.interval_seconds)
    print("Published language NuGet smoke environment", flush=True)
    print(f"  Python        : {platform.python_version()} {platform.platform()}", flush=True)
    print(f"  Machine       : {platform.machine()}", flush=True)
    dotnet_info = run_command(["dotnet", "--info"], env=os.environ.copy())
    print(dotnet_info.stdout, flush=True)

    with tempfile.TemporaryDirectory(prefix="fastparser-published-language-nuget-") as temp:
        project_dir = Path(temp) / "consumer"
        env = os.environ.copy()
        env["NUGET_PACKAGES"] = str(Path(temp) / "packages")
        env.pop("FASTPARSE_LIBRARY_PATH", None)
        env.pop("TSMP_LIBRARY_PATH", None)
        env.pop(f"FASTPARSE_LANGUAGE_{args.language.replace('-', '_').upper()}_PATH", None)

        run_command(
            ["dotnet", "new", "console", "--framework", smoke_framework(env), "--output", str(project_dir)],
            env=env,
        )
        project = str(project_dir / "consumer.csproj")
        run_command(
            ["dotnet", "add", project, "package", CORE_PACKAGE, "--version", core_version, "--source", SOURCE],
            env=env,
        )
        run_command(
            ["dotnet", "add", project, "package", language_package, "--version", args.version, "--source", SOURCE],
            env=env,
        )
        (project_dir / "Program.cs").write_text(smoke_program(args.language), encoding="utf-8")
        completed = run_command(["dotnet", "run", "--project", project], env=env)
        if "FastParser published language NuGet smoke OK" not in completed.stdout:
            raise AssertionError(f"published language NuGet smoke failed:\n{completed.stdout}")

    print(f"Validated published NuGet language package: {language_package} {args.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
