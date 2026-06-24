#!/usr/bin/env python3
"""Validate a FastParse Python wheel from a clean virtual environment."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path


PROGRAM = r'''
import fastparse
from importlib.metadata import version
from fastparse import FastParse
from tsmp import default_library_path

assert fastparse.__version__ == version("fastparse"), (fastparse.__version__, version("fastparse"))

parser = FastParse()
result = parser.parse_bytes(
    b"class Demo { void run() { System.out.println(\"wheel\"); } }",
    language="java",
    output_format="json",
    include_rules=["method_declaration"],
    fields=["rule", "text", "byte_range"],
)
doc = result.json()
assert result.node_count == 1, result.node_count
assert doc["nodes"][0]["rule"] == "method_declaration", doc

diagnostics = parser.parse_bytes(
    b"class Demo { void broken( { }",
    language="java",
    output_format="diagnostics",
)
quality = diagnostics.json()
assert quality["hasErrors"] is True, quality
assert "nodes" not in quality, quality

print("FastParse Python wheel smoke OK")
print(parser.version)
print(default_library_path())
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a FastParse Python wheel.")
    parser.add_argument("wheel", type=Path)
    return parser.parse_args()


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def validate_contents(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as zf:
        names = set(zf.namelist())
    required = {
        "fastparse/__init__.py",
        "fastparse/py.typed",
        "tsmp/__init__.py",
        "tsmp/native.py",
        "tsmp/py.typed",
    }
    missing = sorted(required_name for required_name in required if not any(name.endswith(required_name) for name in names))
    if missing:
        raise AssertionError(f"wheel missing entries: {', '.join(missing)}")
    native = [name for name in names if "fastparse/native/" in name]
    if not native:
        raise AssertionError("wheel does not include a bundled native FastParse library")


def main() -> int:
    args = parse_args()
    wheel = args.wheel.resolve()
    if not wheel.is_file():
        raise FileNotFoundError(wheel)
    validate_contents(wheel)

    with tempfile.TemporaryDirectory(prefix="fastparse-python-wheel-") as temp:
        venv_dir = Path(temp) / "venv"
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        python = venv_python(venv_dir)
        subprocess.run([str(python), "-m", "pip", "install", "--no-index", str(wheel)], check=True)
        completed = subprocess.run(
            [str(python), "-c", PROGRAM],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )
        if "FastParse Python wheel smoke OK" not in completed.stdout:
            raise AssertionError(f"wheel smoke failed:\n{completed.stdout}")

    print(f"Validated Python wheel: {wheel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
