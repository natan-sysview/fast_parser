#!/usr/bin/env python3
"""Validate FastParse.nupkg from a clean consumer project."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import tempfile
from pathlib import Path


PACKAGE_RE = re.compile(r"^FastParse\.(?P<version>.+)\.nupkg$")


PROGRAM = r'''using FastParse;

using var parser = new FastParseClient();

var result = parser.ParseText(
    "class Demo { void run() { System.out.println(\"nuget\"); } }",
    new ParseOptions
    {
        Format = FastParseFormat.Json,
        IncludeRules = "method_declaration",
        Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
    });

if (result.NodeCount != 1 || !result.Text.Contains("method_declaration", StringComparison.Ordinal))
{
    throw new InvalidOperationException("FastParse NuGet smoke test failed.");
}

Console.WriteLine("FastParse NuGet smoke OK");
Console.WriteLine(parser.Version);
Console.WriteLine(parser.LibraryPath);
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a FastParse NuGet package.")
    parser.add_argument("package", type=Path)
    return parser.parse_args()


def package_version(package: Path) -> str:
    match = PACKAGE_RE.match(package.name)
    if not match:
        raise AssertionError(f"unexpected package name: {package.name}")
    return match.group("version")


def main() -> int:
    args = parse_args()
    package = args.package.resolve()
    if not package.is_file():
        raise FileNotFoundError(package)

    version = package_version(package)
    with tempfile.TemporaryDirectory(prefix="fastparse-nuget-smoke-") as temp:
        project_dir = Path(temp) / "consumer"
        env = os.environ.copy()
        env["NUGET_PACKAGES"] = str(Path(temp) / "packages")
        env.pop("FASTPARSE_LIBRARY_PATH", None)
        env.pop("TSMP_LIBRARY_PATH", None)

        subprocess.run(
            ["dotnet", "new", "console", "--framework", "net9.0", "--output", str(project_dir)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True,
        )
        subprocess.run(
            [
                "dotnet",
                "add",
                str(project_dir / "consumer.csproj"),
                "package",
                "FastParse",
                "--version",
                version,
                "--source",
                str(package.parent),
            ],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True,
        )
        (project_dir / "Program.cs").write_text(PROGRAM, encoding="utf-8")

        completed = subprocess.run(
            ["dotnet", "run", "--project", str(project_dir / "consumer.csproj")],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True,
        )
        if "FastParse NuGet smoke OK" not in completed.stdout:
            raise AssertionError(f"NuGet smoke did not report success:\n{completed.stdout}")

    print(f"Validated NuGet package: {package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
