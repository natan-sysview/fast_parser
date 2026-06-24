#!/usr/bin/env python3
"""Validate a published FastParse language extension wheel from PyPI."""

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


CORE_PACKAGE = "fastparse"
LANGUAGE = "python"
LANGUAGE_PACKAGE = "fastparse-language-python"

PROGRAM = r'''
import fastparse
import fastparse_language_python
from importlib.metadata import version
from fastparse import FastParse

assert fastparse.__version__ == version("fastparse"), (fastparse.__version__, version("fastparse"))
assert fastparse_language_python.__version__ == version("fastparse-language-python")

parser = FastParse()
load = parser.load_bundled_language("python")
assert load.language == "python", load
assert parser.language_available("python")

json_result = parser.parse_text(
    "def hello(name):\n    return name\n",
    language="python",
    output_format="json",
    include_rules=["function_definition"],
    fields=["rule", "text", "byte_range"],
)
doc = json_result.json()
assert json_result.node_count == 1, json_result.node_count
assert doc["nodes"][0]["rule"] == "function_definition", doc

diagnostics = parser.parse_text(
    "def broken(\n",
    language="python",
    output_format="diagnostics",
)
quality = diagnostics.json()
assert quality["hasErrors"] is True, quality
assert "nodes" not in quality, quality

print("FastParse published PyPI language smoke OK")
print(fastparse.__version__)
print(fastparse_language_python.__version__)
print(parser.version)
print(fastparse_language_python.extension_path())
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
    parser = argparse.ArgumentParser(description="Validate fastparse-language-python from PyPI.")
    parser.add_argument("--version", required=True, help="FastParse release version or PyPI version.")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--interval-seconds", type=int, default=30)
    return parser.parse_args()


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def published_versions(package: str) -> set[str]:
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{package}/json", timeout=20) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return set()
        raise
    return set(payload.get("releases", {}))


def wait_for_version(package: str, version: str, timeout_seconds: int, interval_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    while True:
        versions = published_versions(package)
        if version in versions:
            return
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{package} {version} was not indexed by PyPI")
        print(f"Waiting for {package} {version} to be indexed by PyPI...", flush=True)
        time.sleep(interval_seconds)


def install_from_pypi(python: Path, version: str, timeout_seconds: int, interval_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    command = [
        str(python),
        "-m",
        "pip",
        "install",
        "--pre",
        "--no-cache-dir",
        "--index-url",
        "https://pypi.org/simple",
        f"{CORE_PACKAGE}=={version}",
        f"{LANGUAGE_PACKAGE}=={version}",
    ]
    while True:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if completed.returncode == 0:
            return
        if time.monotonic() >= deadline:
            raise RuntimeError(f"could not install FastParse language packages from PyPI:\n{completed.stdout}")
        print("Waiting for pip to install FastParse language packages from PyPI...", flush=True)
        print(completed.stdout, flush=True)
        time.sleep(interval_seconds)


def main() -> int:
    args = parse_args()
    version = pypi_version(args.version)
    wait_for_version(CORE_PACKAGE, version, args.timeout_seconds, args.interval_seconds)
    wait_for_version(LANGUAGE_PACKAGE, version, args.timeout_seconds, args.interval_seconds)

    with tempfile.TemporaryDirectory(prefix="fastparse-published-pypi-language-") as temp:
        venv_dir = Path(temp) / "venv"
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        python = venv_python(venv_dir)
        subprocess.run([str(python), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        install_from_pypi(python, version, args.timeout_seconds, args.interval_seconds)
        completed = subprocess.run(
            [str(python), "-c", PROGRAM],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"published PyPI language smoke command failed:\n{completed.stdout}")
        if "FastParse published PyPI language smoke OK" not in completed.stdout:
            raise AssertionError(f"published PyPI language smoke failed:\n{completed.stdout}")

    print(f"Validated published PyPI language package: {LANGUAGE_PACKAGE} {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
