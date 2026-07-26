#!/usr/bin/env python3
"""Validate the FastParse npm package from a clean consumer project."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import tarfile
import tempfile
from pathlib import Path


PACKAGE_NAME = "@natan-sysview/fastparse"
PROGRAM = r'''
const assert = require("node:assert/strict");
const { FastParseClient, OutputFormat } = require("@natan-sysview/fastparse");

const parser = new FastParseClient();
const source = "class Demo { void run() { System.out.println(\"npm\"); } }";

const result = parser.parseText(source, {
  includeRules: ["method_declaration"],
  fields: ["rule", "text", "byte_range"]
});
const doc = result.json();
assert.equal(result.nodeCount, 1);
assert.equal(doc.nodes[0].rule, "method_declaration");

const diagnostics = parser.parseText("class Demo { void broken( { }", {
  outputFormat: "diagnostics"
}).json();
assert.equal(diagnostics.hasErrors, true);
assert.equal("nodes" in diagnostics, false);

const binary = parser.parseText(source, {
  outputFormat: OutputFormat.Binary,
  includeRules: ["method_declaration"],
  fields: ["rule", "text", "byte_range"]
}).binaryDocument();
assert.equal(binary.format, "tsmp-binary");
assert.equal(binary.schemaVersion, 1);

const query = parser.queryText(
  source,
  "(method_declaration name: (identifier) @method.name) @method",
  { fields: ["capture_name", "rule", "text", "range", "byte_range"] }
).json();
assert.ok(query.captureCount >= 2);

console.log("FastParse npm smoke OK");
console.log(parser.version);
console.log(parser.libraryPath);
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a FastParse npm package.")
    parser.add_argument("package", type=Path)
    parser.add_argument("--require-all-platforms", action="store_true")
    return parser.parse_args()


def default_rid() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "darwin":
        os_name = "osx"
    elif system == "windows":
        os_name = "win"
    else:
        os_name = "linux"

    if machine in {"x86_64", "amd64"}:
        arch = "x64"
    elif machine in {"arm64", "aarch64"}:
        arch = "arm64"
    else:
        arch = machine
    return f"{os_name}-{arch}"


def native_name_for_rid(rid: str) -> str:
    if rid.startswith("win-"):
        return "fastparse.dll"
    if rid.startswith("osx-"):
        return "libfastparse.dylib"
    return "libfastparse.so"


def validate_contents(package: Path, require_all_platforms: bool) -> None:
    with tarfile.open(package, "r:gz") as tf:
        names = set(tf.getnames())

    required = {
        "package/package.json",
        "package/dist/index.js",
        "package/dist/index.d.ts",
        "package/dist/native.js",
        "package/docs/typescript_binding.md",
        "package/docs/bindings.md",
        "package/docs/contracts.md",
        "package/docs/binary_schema.md",
        "package/AI_AGENT_GUIDE.md",
        "package/README.md",
        "package/LICENSE",
    }
    if require_all_platforms:
        for rid in ["linux-x64", "osx-arm64", "osx-x64", "win-x64"]:
            required.add(f"package/runtimes/{rid}/native/{native_name_for_rid(rid)}")
    else:
        rid = default_rid()
        required.add(f"package/runtimes/{rid}/native/{native_name_for_rid(rid)}")

    missing = sorted(required - names)
    if missing:
        raise AssertionError(f"npm package missing entries: {', '.join(missing)}")


def main() -> int:
    args = parse_args()
    package = args.package.resolve()
    if not package.is_file():
        raise FileNotFoundError(package)
    validate_contents(package, args.require_all_platforms)

    with tempfile.TemporaryDirectory(prefix="fastparse-npm-smoke-") as temp:
        project = Path(temp) / "consumer"
        project.mkdir()
        (project / "package.json").write_text(
            json.dumps({"name": "fastparse-npm-smoke", "private": True, "type": "commonjs"}, indent=2) + "\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env.pop("FASTPARSE_LIBRARY_PATH", None)
        env.pop("TSMP_LIBRARY_PATH", None)
        subprocess.run(["npm", "install", str(package)], cwd=project, env=env, check=True)
        completed = subprocess.run(
            ["node", "-e", PROGRAM],
            cwd=project,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )
        if "FastParse npm smoke OK" not in completed.stdout:
            raise AssertionError(f"npm smoke did not report success:\n{completed.stdout}")

    print(f"Validated npm package: {package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
