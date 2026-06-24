#!/usr/bin/env python3
"""Validate a published FastParse wheel from PyPI."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import venv
from pathlib import Path


PACKAGE_NAME = "fastparse"
PYPI_JSON_URL = "https://pypi.org/pypi/fastparse/json"

PROGRAM = r'''
import fastparse
from importlib.metadata import version
from fastparse import FastParse, Field, OutputFormat, ParseOptions
from tsmp import default_library_path

assert fastparse.__version__ == version("fastparse"), (fastparse.__version__, version("fastparse"))

parser = FastParse()
json_result = parser.parse_bytes(
    b"class Demo { void run() { System.out.println(\"pypi\"); } }",
    language="java",
    output_format="json",
    include_rules=["method_declaration"],
    fields=["rule", "text", "byte_range"],
)
doc = json_result.json()
assert json_result.node_count == 1, json_result.node_count
assert doc["nodes"][0]["rule"] == "method_declaration", doc

binary_result = parser.parse_bytes(
    b"class Demo { void run() { System.out.println(\"pypi\"); } }",
    ParseOptions(
        output_format=OutputFormat.BINARY,
        include_rules=["method_declaration"],
        fields=Field.RULE | Field.TEXT,
    ),
)
assert binary_result.node_count == 1, binary_result.node_count
assert binary_result.data and b"tsmp-binary" in binary_result.data, binary_result.data[:32]
binary_doc = binary_result.binary_document()
assert binary_doc.nodes[0].rule == "method_declaration", binary_doc

diagnostics = parser.parse_bytes(
    b"class Demo { void broken( { }",
    language="java",
    output_format="diagnostics",
)
quality = diagnostics.json()
assert quality["hasErrors"] is True, quality
assert "nodes" not in quality, quality

print("FastParse published PyPI smoke OK")
print(fastparse.__version__)
print(parser.version)
print(default_library_path())
'''


def pypi_version(release_version: str) -> str:
    if "-preview." in release_version:
        base, preview = release_version.split("-preview.", 1)
        return f"{base}rc{preview}"
    if "-preview" in release_version:
        base, preview = release_version.split("-preview", 1)
        return f"{base}rc{preview.lstrip('.') or '0'}"
    return release_version


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate FastParse from PyPI.")
    parser.add_argument("--version", required=True, help="FastParse release version or PyPI version.")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--interval-seconds", type=int, default=30)
    return parser.parse_args()


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def published_versions() -> set[str]:
    try:
        with urllib.request.urlopen(PYPI_JSON_URL, timeout=20) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return set()
        raise
    return set(payload.get("releases", {}))


def wait_for_version(version: str, timeout_seconds: int, interval_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    while True:
        versions = published_versions()
        if version in versions:
            return
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{PACKAGE_NAME} {version} was not indexed by PyPI")
        print(f"Waiting for {PACKAGE_NAME} {version} to be indexed by PyPI...", flush=True)
        time.sleep(interval_seconds)


def main() -> int:
    args = parse_args()
    version = pypi_version(args.version)
    wait_for_version(version, args.timeout_seconds, args.interval_seconds)

    with tempfile.TemporaryDirectory(prefix="fastparse-published-pypi-") as temp:
        venv_dir = Path(temp) / "venv"
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        python = venv_python(venv_dir)
        subprocess.run([str(python), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([str(python), "-m", "pip", "install", f"{PACKAGE_NAME}=={version}"], check=True)
        completed = subprocess.run(
            [str(python), "-c", PROGRAM],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"published PyPI smoke command failed:\n{completed.stdout}")
        if "FastParse published PyPI smoke OK" not in completed.stdout:
            raise AssertionError(f"published PyPI smoke failed:\n{completed.stdout}")

    print(f"Validated published PyPI package: {PACKAGE_NAME} {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
