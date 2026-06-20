#!/usr/bin/env python3
"""Validate a FastParse release archive as an end user would use it."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Any


SAMPLE_SOURCE = b"class Demo { void run() { System.out.println(\"fastparse\"); } }"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a FastParse release package.")
    parser.add_argument("archive", type=Path)
    parser.add_argument("--platform", choices=("linux", "macos", "windows"), required=True)
    parser.add_argument("--skip-example", action="store_true")
    return parser.parse_args()


def library_relative_path(platform_name: str) -> Path:
    if platform_name == "windows":
        return Path("bin") / "fastparse.dll"
    if platform_name == "macos":
        return Path("lib") / "libfastparse.dylib"
    return Path("lib") / "libfastparse.so"


def extract_archive(archive: Path, destination: Path) -> Path:
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(destination)
    elif archive.name.endswith(".tar.gz"):
        with tarfile.open(archive, "r:gz") as tf:
            try:
                tf.extractall(destination, filter="data")
            except TypeError:
                tf.extractall(destination)
    else:
        raise ValueError(f"unsupported archive type: {archive}")

    package_roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(package_roots) != 1:
        raise AssertionError(f"expected one package root, found {len(package_roots)}")
    return package_roots[0]


def require_file(path: Path) -> None:
    if not path.is_file():
        raise AssertionError(f"missing file: {path}")


def require_directory(path: Path) -> None:
    if not path.is_dir():
        raise AssertionError(f"missing directory: {path}")


def validate_manifest(package_dir: Path, *, platform_name: str, library_path: Path) -> None:
    manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
    expected_library = library_path.relative_to(package_dir).as_posix()
    expected = {
        "name": "fastparse",
        "platform": platform_name,
        "library": expected_library,
        "c_api": "fastparse-c-api/0.3.0",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise AssertionError(f"manifest {key!r} expected {value!r}, found {manifest.get(key)!r}")
    for key in ("version", "arch", "formats", "bindings", "headers", "docs"):
        if key not in manifest:
            raise AssertionError(f"manifest missing key: {key}")


def validate_layout(package_dir: Path, platform_name: str) -> Path:
    print("Validating package layout...", flush=True)
    library_path = package_dir / library_relative_path(platform_name)
    for path in [
        package_dir / "README.md",
        package_dir / "LICENSE",
        package_dir / "RELEASE.md",
        package_dir / "manifest.json",
        package_dir / "smoke_test.py",
        package_dir / "include" / "fastparse.h",
        package_dir / "include" / "tsmp.h",
        package_dir / "bindings" / "python" / "tsmp" / "native.py",
        package_dir / "examples" / "python" / "01_parse_string" / "parse_string.py",
        package_dir / "docs" / "contracts.md",
        library_path,
    ]:
        require_file(path)

    for path in [
        package_dir / "bindings",
        package_dir / "docs",
        package_dir / "examples",
        package_dir / "include",
    ]:
        require_directory(path)
    validate_manifest(package_dir, platform_name=platform_name, library_path=library_path)
    return library_path


def import_binding(package_dir: Path) -> Any:
    sys.path.insert(0, str(package_dir / "bindings" / "python"))
    from tsmp import Tsmp  # noqa: WPS433

    return Tsmp


def validate_python_binding(package_dir: Path, library_path: Path) -> None:
    print("Validating Python binding parse contracts...", flush=True)
    Tsmp = import_binding(package_dir)
    parser = Tsmp(library_path)

    json_result = parser.parse_bytes(
        SAMPLE_SOURCE,
        output_format="json",
        include_rules=["class_declaration", "method_declaration"],
        fields=["rule", "text", "byte_range"],
    )
    document = json.loads(json_result.data)
    rules = [node["rule"] for node in document["nodes"]]
    if rules != ["class_declaration", "method_declaration"]:
        raise AssertionError(f"unexpected JSON rules: {rules}")

    binary_result = parser.parse_bytes(
        SAMPLE_SOURCE,
        output_format="binary",
        include_rules=["method_declaration"],
        fields=["rule", "text"],
    )
    if binary_result.node_count != 1 or len(binary_result.data) == 0:
        raise AssertionError("binary parse did not return one populated method node")

    stats_result = parser.parse_bytes(SAMPLE_SOURCE, output_format="stats")
    if stats_result.node_count <= 0 or stats_result.data != b"":
        raise AssertionError("stats parse contract failed")


def validate_python_example(package_dir: Path, library_path: Path) -> None:
    print("Validating packaged Python example...", flush=True)
    example = package_dir / "examples" / "python" / "01_parse_string" / "parse_string.py"
    env = os.environ.copy()
    env["FASTPARSE_LIBRARY_PATH"] = str(library_path)
    env["PYTHONPATH"] = str(package_dir / "bindings" / "python")
    env.pop("TSMP_LIBRARY_PATH", None)
    completed = subprocess.run(
        [
            sys.executable,
            str(example),
            "--lib",
            str(library_path),
            "--format",
            "json",
            "--rules",
            "method_declaration",
            "--fields",
            "rule,text",
            "--summary",
        ],
        env=env,
        cwd=package_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    if "method_declaration" not in completed.stdout:
        raise AssertionError(f"example output did not include method_declaration:\n{completed.stdout}")


def validate_smoke_test(package_dir: Path, library_path: Path) -> None:
    print("Validating packaged smoke test...", flush=True)
    smoke_test = package_dir / "smoke_test.py"
    env = os.environ.copy()
    env["FASTPARSE_LIBRARY_PATH"] = str(library_path)
    env["PYTHONPATH"] = str(package_dir / "bindings" / "python")
    env.pop("TSMP_LIBRARY_PATH", None)
    completed = subprocess.run(
        [sys.executable, str(smoke_test), "--lib", str(library_path)],
        env=env,
        cwd=package_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    if "FastParse smoke test OK" not in completed.stdout:
        raise AssertionError(f"smoke test did not report success:\n{completed.stdout}")


def main() -> int:
    args = parse_args()
    archive = args.archive.resolve()
    if not archive.is_file():
        raise FileNotFoundError(archive)

    with tempfile.TemporaryDirectory(prefix="fastparse-package-", ignore_cleanup_errors=True) as temp:
        temp_dir = Path(temp)
        package_dir = extract_archive(archive, temp_dir)
        library_path = validate_layout(package_dir, args.platform)
        validate_python_binding(package_dir, library_path)
        validate_smoke_test(package_dir, library_path)
        if not args.skip_example:
            validate_python_example(package_dir, library_path)
        print(f"Validated package: {archive.name}")
        print(f"Package root     : {package_dir.name}")
        print(f"Native library   : {library_path.relative_to(package_dir)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
