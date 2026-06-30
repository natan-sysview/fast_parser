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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a FastParser.Language.* package from nuget.org.")
    parser.add_argument("--version", required=True)
    parser.add_argument("--language", default="python")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--interval-seconds", type=int, default=30)
    return parser.parse_args()


def package_language_name(language: str) -> str:
    return "".join(part.capitalize() for part in language.replace("-", "_").split("_"))


def package_id(language: str) -> str:
    return f"FastParser.Language.{package_language_name(language)}"


def package_index_url(language: str) -> str:
    return f"https://api.nuget.org/v3-flatcontainer/{package_id(language).lower()}/index.json"


def smoke_program(language: str) -> str:
    if language == "java-frameworks":
        return JAVA_FRAMEWORKS_PROGRAM
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
    language_package = package_id(args.language)
    language_index_url = package_index_url(args.language)
    wait_for_version(CORE_PACKAGE, CORE_INDEX_URL, args.version, args.timeout_seconds, args.interval_seconds)
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
            ["dotnet", "new", "console", "--framework", "net9.0", "--output", str(project_dir)],
            env=env,
        )
        project = str(project_dir / "consumer.csproj")
        run_command(
            ["dotnet", "add", project, "package", CORE_PACKAGE, "--version", args.version, "--source", SOURCE],
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
