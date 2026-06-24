#!/usr/bin/env python3
"""Validate a local FastParser language extension NuGet package."""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


SOURCE = "https://api.nuget.org/v3/index.json"

PROGRAM = r'''using FastParse;

using var parser = new FastParseClient();

var load = parser.LoadBundledLanguage("python");
if (load.Language != "python" || !parser.LanguageAvailable("python"))
{
    throw new InvalidOperationException("FastParser.Language.Python load smoke failed");
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
    throw new InvalidOperationException("FastParser.Language.Python JSON smoke failed");
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
    throw new InvalidOperationException("FastParser.Language.Python diagnostics smoke failed");
}

Console.WriteLine("FastParser language NuGet smoke OK");
Console.WriteLine(parser.Version);
Console.WriteLine(parser.LibraryPath);
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate FastParser.Language.Python from local nupkgs.")
    parser.add_argument("--core-package", type=Path, required=True)
    parser.add_argument("--language-package", type=Path, required=True)
    parser.add_argument("--version", required=True)
    return parser.parse_args()


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


def validate_package_layout(language_package: Path) -> None:
    required = {
        "README.md",
        "contentFiles/any/any/fastparse/languages/python/manifest.json",
        "buildTransitive/FastParser.Language.Python.targets",
        "runtimes/linux-x64/native/libfastparse_language_python.so",
        "runtimes/osx-arm64/native/libfastparse_language_python.dylib",
        "runtimes/osx-x64/native/libfastparse_language_python.dylib",
        "runtimes/win-x64/native/fastparse_language_python.dll",
    }
    with zipfile.ZipFile(language_package) as zf:
        names = set(zf.namelist())
    missing = sorted(required - names)
    if missing:
        raise AssertionError(f"language NuGet package missing entries: {', '.join(missing)}")


def main() -> int:
    args = parse_args()
    core_package = args.core_package.resolve()
    language_package = args.language_package.resolve()
    if not core_package.is_file():
        raise FileNotFoundError(core_package)
    if not language_package.is_file():
        raise FileNotFoundError(language_package)
    validate_package_layout(language_package)

    print("Local language NuGet smoke environment", flush=True)
    print(f"  Python  : {platform.python_version()} {platform.platform()}", flush=True)
    print(f"  Machine : {platform.machine()}", flush=True)
    dotnet_info = run_command(["dotnet", "--info"], env=os.environ.copy())
    print(dotnet_info.stdout, flush=True)

    with tempfile.TemporaryDirectory(prefix="fastparser-language-nuget-smoke-") as temp:
        temp_dir = Path(temp)
        package_source = temp_dir / "packages"
        package_source.mkdir()
        shutil.copy2(core_package, package_source / core_package.name)
        shutil.copy2(language_package, package_source / language_package.name)

        project_dir = temp_dir / "consumer"
        env = os.environ.copy()
        env["NUGET_PACKAGES"] = str(temp_dir / "global-packages")
        env.pop("FASTPARSE_LIBRARY_PATH", None)
        env.pop("TSMP_LIBRARY_PATH", None)
        env.pop("FASTPARSE_LANGUAGE_PYTHON_PATH", None)

        run_command(
            ["dotnet", "new", "console", "--framework", "net9.0", "--output", str(project_dir)],
            env=env,
        )
        project = str(project_dir / "consumer.csproj")
        run_command(
            ["dotnet", "add", project, "package", "FastParser", "--version", args.version, "--source", str(package_source)],
            env=env,
        )
        run_command(
            [
                "dotnet",
                "add",
                project,
                "package",
                "FastParser.Language.Python",
                "--version",
                args.version,
                "--source",
                str(package_source),
                "--source",
                SOURCE,
            ],
            env=env,
        )
        (project_dir / "Program.cs").write_text(PROGRAM, encoding="utf-8")
        completed = run_command(["dotnet", "run", "--project", project], env=env)
        if "FastParser language NuGet smoke OK" not in completed.stdout:
            raise AssertionError(f"language NuGet smoke failed:\n{completed.stdout}")

    print(f"Validated local language NuGet package: {language_package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
