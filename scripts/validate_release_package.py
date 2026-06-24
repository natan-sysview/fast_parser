#!/usr/bin/env python3
"""Validate a FastParse release archive as an end user would use it."""

from __future__ import annotations

import argparse
import json
import os
import shutil
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
    parser.add_argument("--skip-csharp-example", action="store_true")
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
    expected_link_library = "bin/fastparse.lib" if platform_name == "windows" else None
    expected = {
        "name": "fastparse",
        "platform": platform_name,
        "library": expected_library,
        "link_library": expected_link_library,
        "c_api": "fastparse-c-api/0.5.0",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise AssertionError(f"manifest {key!r} expected {value!r}, found {manifest.get(key)!r}")
    for key in ("version", "arch", "formats", "normalization", "bindings", "headers", "docs"):
        if key not in manifest:
            raise AssertionError(f"manifest missing key: {key}")


def validate_layout(package_dir: Path, platform_name: str) -> Path:
    print("Validating package layout...", flush=True)
    library_path = package_dir / library_relative_path(platform_name)
    required_files = [
        package_dir / "README.md",
        package_dir / "GETTING_STARTED.md",
        package_dir / "LICENSE",
        package_dir / "RELEASE.md",
        package_dir / "manifest.json",
        package_dir / "smoke_test.py",
        package_dir / "include" / "fastparse.h",
        package_dir / "include" / "tsmp.h",
        package_dir / "bindings" / "python" / "tsmp" / "native.py",
        package_dir / "examples" / "c" / "parse_string.c",
        package_dir / "examples" / "python" / "01_parse_string" / "parse_string.py",
        package_dir / "docs" / "contracts.md",
        library_path,
    ]
    if platform_name == "windows":
        required_files.append(package_dir / "bin" / "fastparse.lib")

    for path in required_files:
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


def validate_c_example(package_dir: Path, platform_name: str, library_path: Path) -> None:
    print("Validating packaged C example...", flush=True)
    source = package_dir / "examples" / "c" / "parse_string.c"
    include_dir = package_dir / "include"
    build_dir = package_dir / ".fastparse-c-smoke-build"
    link_library = package_dir / "bin" / "fastparse.lib"

    imported_properties = [
        f'IMPORTED_LOCATION "{library_path.as_posix()}"',
        f'INTERFACE_INCLUDE_DIRECTORIES "{include_dir.as_posix()}"',
    ]
    if platform_name == "windows":
        imported_properties.append(f'IMPORTED_IMPLIB "{link_library.as_posix()}"')

    cmake_lists = f"""cmake_minimum_required(VERSION 3.20)
project(fastparse_package_c_smoke C)

add_executable(fastparse_c_smoke "{source.as_posix()}")
add_library(fastparse_native SHARED IMPORTED GLOBAL)
set_target_properties(fastparse_native PROPERTIES
    {' '.join(imported_properties)}
)
target_link_libraries(fastparse_c_smoke PRIVATE fastparse_native)
if(APPLE OR UNIX)
    set_target_properties(fastparse_c_smoke PROPERTIES BUILD_RPATH "{library_path.parent.as_posix()}")
endif()
"""
    build_dir.mkdir(exist_ok=True)

    (package_dir / "CMakeLists.txt").write_text(cmake_lists, encoding="utf-8")
    subprocess.run(
        ["cmake", "-S", str(package_dir), "-B", str(build_dir), "-DCMAKE_BUILD_TYPE=Release"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=True,
    )
    subprocess.run(
        ["cmake", "--build", str(build_dir), "--config", "Release"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=True,
    )

    exe_name = "fastparse_c_smoke.exe" if platform_name == "windows" else "fastparse_c_smoke"
    candidates = list(build_dir.rglob(exe_name))
    if not candidates:
        raise AssertionError(f"C smoke executable not found under {build_dir}")
    executable = candidates[0]

    env = os.environ.copy()
    if platform_name == "windows":
        env["PATH"] = f"{library_path.parent}{os.pathsep}{env.get('PATH', '')}"
    elif platform_name == "macos":
        env["DYLD_LIBRARY_PATH"] = f"{library_path.parent}{os.pathsep}{env.get('DYLD_LIBRARY_PATH', '')}"
    else:
        env["LD_LIBRARY_PATH"] = f"{library_path.parent}{os.pathsep}{env.get('LD_LIBRARY_PATH', '')}"

    completed = subprocess.run(
        [str(executable)],
        env=env,
        cwd=package_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    if "FastParse C smoke test OK" not in completed.stdout:
        raise AssertionError(f"C smoke test did not report success:\n{completed.stdout}")


def validate_csharp_example(package_dir: Path, library_path: Path) -> None:
    print("Validating packaged C# example...", flush=True)
    if shutil.which("dotnet") is None:
        raise AssertionError("dotnet was not found; pass --skip-csharp-example to skip this optional check")

    project = package_dir / "examples" / "csharp" / "01_parse_string" / "FastParse.ParseStringExample.csproj"
    require_file(project)

    env = os.environ.copy()
    env["FASTPARSE_LIBRARY_PATH"] = str(library_path)
    env.pop("TSMP_LIBRARY_PATH", None)

    subprocess.run(
        ["dotnet", "build", str(project), "--nologo"],
        env=env,
        cwd=package_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    completed = subprocess.run(
        ["dotnet", "run", "--no-build", "--project", str(project)],
        env=env,
        cwd=package_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    if "C# smoke OK" not in completed.stdout:
        raise AssertionError(f"C# smoke test did not report success:\n{completed.stdout}")


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
        validate_c_example(package_dir, args.platform, library_path)
        if not args.skip_csharp_example:
            validate_csharp_example(package_dir, library_path)
        validate_smoke_test(package_dir, library_path)
        if not args.skip_example:
            validate_python_example(package_dir, library_path)
        print(f"Validated package: {archive.name}")
        print(f"Package root     : {package_dir.name}")
        print(f"Native library   : {library_path.relative_to(package_dir)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
