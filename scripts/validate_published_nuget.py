#!/usr/bin/env python3
"""Validate a published FastParser package from nuget.org."""

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


PACKAGE_ID = "FastParser"
SOURCE = "https://api.nuget.org/v3/index.json"
INDEX_URL = "https://api.nuget.org/v3-flatcontainer/fastparser/index.json"

PROGRAM = r'''using FastParse;

using var parser = new FastParseClient();

var json = parser.ParseText(
    "class Demo { void run() { System.out.println(\"published\"); } }",
    new ParseOptions
    {
        Format = FastParseFormat.Json,
        IncludeRules = "method_declaration",
        Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
    });

if (json.NodeCount != 1 || !json.Text.Contains("method_declaration", StringComparison.Ordinal))
{
    throw new InvalidOperationException("published NuGet JSON smoke failed");
}

var binary = parser.ParseText(
    "class Demo { void run() { System.out.println(\"published\"); } }",
    new ParseOptions
    {
        Format = FastParseFormat.Binary,
        IncludeRules = "method_declaration",
        Fields = FastParseField.Rule | FastParseField.Text
    });

var document = FastParseMessagePack.Decode(binary.Data);
if (document.Nodes.Count != 1 || document.Nodes[0].Rule != "method_declaration")
{
    throw new InvalidOperationException("published NuGet binary smoke failed");
}

Console.WriteLine("FastParser published NuGet smoke OK");
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
    parser = argparse.ArgumentParser(description="Validate FastParser from nuget.org.")
    parser.add_argument("--version", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--interval-seconds", type=int, default=30)
    return parser.parse_args()


def published_versions() -> set[str]:
    try:
        with urllib.request.urlopen(INDEX_URL) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return set()
        raise
    return set(payload.get("versions", []))


def wait_for_version(version: str, timeout_seconds: int, interval_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    while True:
        versions = published_versions()
        if version in versions:
            return
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{PACKAGE_ID} {version} was not indexed by nuget.org")
        print(f"Waiting for {PACKAGE_ID} {version} to be indexed by nuget.org...", flush=True)
        time.sleep(interval_seconds)


def main() -> int:
    args = parse_args()
    wait_for_version(args.version.lower(), args.timeout_seconds, args.interval_seconds)
    print("Published NuGet smoke environment", flush=True)
    print(f"  Python        : {platform.python_version()} {platform.platform()}", flush=True)
    print(f"  Machine       : {platform.machine()}", flush=True)
    dotnet_info = run_command(["dotnet", "--info"], env=os.environ.copy())
    print(dotnet_info.stdout, flush=True)

    with tempfile.TemporaryDirectory(prefix="fastparser-published-nuget-") as temp:
        project_dir = Path(temp) / "consumer"
        env = os.environ.copy()
        env["NUGET_PACKAGES"] = str(Path(temp) / "packages")
        env.pop("FASTPARSE_LIBRARY_PATH", None)
        env.pop("TSMP_LIBRARY_PATH", None)

        run_command(
            ["dotnet", "new", "console", "--framework", "net9.0", "--output", str(project_dir)],
            env=env,
        )
        run_command(
            [
                "dotnet",
                "add",
                str(project_dir / "consumer.csproj"),
                "package",
                PACKAGE_ID,
                "--version",
                args.version,
                "--source",
                SOURCE,
            ],
            env=env,
        )
        (project_dir / "Program.cs").write_text(PROGRAM, encoding="utf-8")
        print("Consumer project assets:", flush=True)
        for path in sorted(project_dir.rglob("*")):
            if path.is_file() and ("FastParse" in path.name or "fastparse" in path.name or path.suffix in {".json", ".csproj"}):
                print(f"  {path.relative_to(project_dir)}", flush=True)

        completed = run_command(
            ["dotnet", "run", "--project", str(project_dir / "consumer.csproj")],
            env=env,
        )
        if "FastParser published NuGet smoke OK" not in completed.stdout:
            raise AssertionError(f"published NuGet smoke failed:\n{completed.stdout}")

    print(f"Validated published NuGet package: {PACKAGE_ID} {args.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
