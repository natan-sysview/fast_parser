#!/usr/bin/env python3
"""Validate a fastparse-language-<language> wheel from a clean venv."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


PROGRAM = r'''
from fastparse import FastParse, OutputFormat, ParseOptions

parser = FastParse()
load = parser.load_bundled_language("python")
assert load.language == "python", load
result = parser.parse_text(
    "def run(value):\n    return value + 1\n",
    ParseOptions(language="python", output_format=OutputFormat.JSON, include_rules=["function_definition"], fields=["rule", "text"]),
)
assert result.node_count == 1, result.node_count
assert "function_definition" in result.text
diagnostics = parser.parse_text("def broken(:\n    pass\n", language="python", output_format=OutputFormat.DIAGNOSTICS).json()
assert diagnostics["hasErrors"]
print("fastparse-language-python wheel smoke OK")
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate fastparse language wheel.")
    parser.add_argument("fastparse_wheel", type=Path)
    parser.add_argument("language_wheel", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with tempfile.TemporaryDirectory(prefix="fastparse-language-wheel-smoke-") as temp:
        venv = Path(temp) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        python = venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        subprocess.run([str(python), "-m", "pip", "install", str(args.fastparse_wheel), str(args.language_wheel)], check=True)
        completed = subprocess.run([str(python), "-c", PROGRAM], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        if "wheel smoke OK" not in completed.stdout:
            raise AssertionError(completed.stdout)
    print(f"Validated Python language wheel: {args.language_wheel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
