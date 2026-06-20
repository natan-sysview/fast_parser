#!/usr/bin/env python3
"""Create a FastParse release archive from a built checkout."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
C_API_VERSION = "fastparse-c-api/0.3.0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package FastParse release artifacts.")
    parser.add_argument("--version", default="0.1.0-preview")
    parser.add_argument("--platform", default=default_platform())
    parser.add_argument("--arch", default=default_arch())
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build")
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--skip-build", action="store_true")
    return parser.parse_args()


def default_platform() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    if system == "windows":
        return "windows"
    if system == "linux":
        return "linux"
    return system


def default_arch() -> str:
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        return "x64"
    if machine in {"arm64", "aarch64"}:
        return "arm64"
    return machine


def library_name(target_platform: str) -> str:
    if target_platform == "windows":
        return "fastparse.dll"
    if target_platform == "macos":
        return "libfastparse.dylib"
    return "libfastparse.so"


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def build(build_dir: Path) -> None:
    run(["cmake", "-S", str(ROOT), "-B", str(build_dir), "-DCMAKE_BUILD_TYPE=Release"])
    run(["cmake", "--build", str(build_dir), "--config", "Release"])


def copy_tree(src: Path, dst: Path) -> None:
    ignore = shutil.ignore_patterns(
        "__pycache__",
        "*.pyc",
        "bin",
        "obj",
        ".DS_Store",
        "*.sqlite",
        "*.sqlite-shm",
        "*.sqlite-wal",
    )
    shutil.copytree(src, dst, ignore=ignore)


def copy_files(package_dir: Path, target_platform: str) -> None:
    lib_name = library_name(target_platform)
    built_library = find_built_library(lib_name)
    if built_library is None:
        raise FileNotFoundError(f"Built library not found: {built_library}")

    binary_dir = package_dir / ("bin" if target_platform == "windows" else "lib")
    binary_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(built_library, binary_dir / lib_name)

    copy_tree(ROOT / "include", package_dir / "include")
    copy_tree(ROOT / "bindings", package_dir / "bindings")
    copy_tree(ROOT / "examples", package_dir / "examples")
    copy_tree(ROOT / "docs", package_dir / "docs")

    for name in [
        "README.md",
        "LICENSE",
        "NOTICE",
        "THIRD_PARTY_NOTICES.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
    ]:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, package_dir / name)


def find_built_library(lib_name: str) -> Path | None:
    direct = ROOT / "bin" / lib_name
    if direct.is_file():
        return direct
    for candidate in (ROOT / "bin").rglob(lib_name):
        if candidate.is_file():
            return candidate
    for candidate in (ROOT / "build").rglob(lib_name):
        if candidate.is_file():
            return candidate
    return None


def write_manifest(package_dir: Path, *, version: str, target_platform: str, arch: str) -> None:
    library = f"{'bin' if target_platform == 'windows' else 'lib'}/{library_name(target_platform)}"
    manifest_json = {
        "name": "fastparse",
        "version": version,
        "platform": target_platform,
        "arch": arch,
        "library": library,
        "c_api": C_API_VERSION,
        "headers": ["include/fastparse.h", "include/tsmp.h"],
        "formats": ["json", "csv", "stats", "binary"],
        "bindings": ["python", "csharp"],
        "docs": ["README.md", "docs/contracts.md", "docs/c_api.md", "docs/output_formats.md"],
    }
    (package_dir / "manifest.json").write_text(
        json.dumps(manifest_json, indent=2) + "\n",
        encoding="utf-8",
    )

    manifest = f"""# FastParse Release

version: {version}
platform: {target_platform}
arch: {arch}
c_api: {C_API_VERSION}

Native library:

```text
{library}
```

Set `FASTPARSE_LIBRARY_PATH` to this library when using bindings from outside this package layout.

Quick smoke test:

```bash
python smoke_test.py
```
"""
    (package_dir / "RELEASE.md").write_text(manifest, encoding="utf-8")


def write_smoke_test(package_dir: Path) -> None:
    smoke_test = r'''#!/usr/bin/env python3
"""End-user smoke test for an unpacked FastParse package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from tsmp import Tsmp, default_library_path  # noqa: E402


SAMPLE_SOURCE = b"class Demo { void run() { System.out.println(\"fastparse\"); } }"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a FastParse package smoke test.")
    parser.add_argument("--lib", type=Path, default=default_library_path())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    parser = Tsmp(args.lib.resolve())
    result = parser.parse_bytes(
        SAMPLE_SOURCE,
        language="java",
        output_format="json",
        include_rules=["method_declaration"],
        fields=["rule", "text", "byte_range"],
    )
    document = json.loads(result.data)
    nodes = document.get("nodes", [])
    if len(nodes) != 1 or nodes[0].get("rule") != "method_declaration":
        raise RuntimeError(f"unexpected parse result: {document}")
    print("FastParse smoke test OK")
    print(f"Library : {parser.version}")
    print(f"Nodes   : {result.node_count}")
    print(f"Rule    : {nodes[0]['rule']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
    path = package_dir / "smoke_test.py"
    path.write_text(smoke_test, encoding="utf-8")
    path.chmod(0o755)


def make_archive(package_dir: Path, dist_dir: Path, target_platform: str) -> Path:
    if target_platform == "windows":
        archive = dist_dir / f"{package_dir.name}.zip"
        if archive.exists():
            archive.unlink()
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in package_dir.rglob("*"):
                zf.write(path, path.relative_to(package_dir.parent))
        return archive

    archive = dist_dir / f"{package_dir.name}.tar.gz"
    if archive.exists():
        archive.unlink()
    with tarfile.open(archive, "w:gz") as tf:
        tf.add(package_dir, arcname=package_dir.name)
    return archive


def main() -> int:
    args = parse_args()
    target_platform = args.platform.lower()
    arch = args.arch.lower()

    if not args.skip_build:
        build(args.build_dir.resolve())

    package_name = f"fastparse-{args.version}-{target_platform}-{arch}"
    package_dir = args.dist_dir.resolve() / package_name
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    copy_files(package_dir, target_platform)
    write_manifest(package_dir, version=args.version, target_platform=target_platform, arch=arch)
    write_smoke_test(package_dir)
    archive = make_archive(package_dir, args.dist_dir.resolve(), target_platform)

    print(f"Package directory: {package_dir}")
    print(f"Archive          : {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
