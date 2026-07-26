#!/usr/bin/env python3
"""Build the FastParse npm package with native runtime assets."""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "bindings" / "typescript"
ARCHIVE_RE = re.compile(r"^fastparse-(?P<version>.+)-(?P<platform>linux|macos|windows)-(?P<arch>x64|arm64)\.(?P<ext>tar\.gz|zip)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build @natan-sysview/fastparse npm package.")
    parser.add_argument("--version", required=True, help="npm package version, for example 0.1.0 or 0.1.0-preview.32")
    parser.add_argument("--archive", action="append", type=Path, default=[], help="FastParse native release archive. May be passed multiple times.")
    parser.add_argument(
        "--native-library",
        action="append",
        default=[],
        metavar="RID=PATH",
        help="Native library for local packaging, for example osx-arm64=bin/libfastparse.dylib.",
    )
    parser.add_argument("--include-current-native", action="store_true", help="Stage the current platform library from bin/ when available.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "npm")
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


def rid_for(platform_name: str, arch: str) -> str:
    prefix = {"linux": "linux", "macos": "osx", "windows": "win"}[platform_name]
    return f"{prefix}-{arch}"


def archive_native_relative(platform_name: str) -> Path:
    if platform_name == "windows":
        return Path("bin") / "fastparse.dll"
    if platform_name == "macos":
        return Path("lib") / "libfastparse.dylib"
    return Path("lib") / "libfastparse.so"


def extract_archive(archive: Path, destination: Path) -> Path:
    if archive.name.endswith(".tar.gz"):
        with tarfile.open(archive, "r:gz") as tf:
            try:
                tf.extractall(destination, filter="data")
            except TypeError:
                tf.extractall(destination)
    elif archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(destination)
    else:
        raise ValueError(f"unsupported archive type: {archive}")

    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise AssertionError(f"expected one package root in {archive}, found {len(roots)}")
    return roots[0]


def parse_native_library_spec(spec: str) -> tuple[str, Path]:
    if "=" not in spec:
        raise ValueError(f"--native-library must be RID=PATH, got: {spec}")
    rid, raw_path = spec.split("=", 1)
    rid = rid.strip()
    if not rid:
        raise ValueError(f"native RID is empty in: {spec}")
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    return rid, path


def current_native_library() -> tuple[str, Path] | None:
    rid = default_rid()
    candidate = ROOT / "bin" / native_name_for_rid(rid)
    if candidate.is_file():
        return rid, candidate
    return None


def stage_native_assets(stage: Path, args: argparse.Namespace) -> set[str]:
    staged: set[str] = set()

    for spec in args.native_library:
        rid, native = parse_native_library_spec(spec)
        copy_native(stage, rid, native)
        staged.add(rid)

    if args.include_current_native:
        current = current_native_library()
        if current is None:
            raise FileNotFoundError(f"current native library not found under {ROOT / 'bin'}")
        rid, native = current
        copy_native(stage, rid, native)
        staged.add(rid)

    for archive in args.archive:
        archive = archive.resolve()
        match = ARCHIVE_RE.match(archive.name)
        if not match:
            raise AssertionError(f"archive does not match FastParse release naming: {archive.name}")
        platform_name = match.group("platform")
        arch = match.group("arch")
        rid = rid_for(platform_name, arch)
        with tempfile.TemporaryDirectory(prefix="fastparse-npm-archive-") as temp:
            package_root = extract_archive(archive, Path(temp))
            native = package_root / archive_native_relative(platform_name)
            copy_native(stage, rid, native)
            staged.add(rid)

    if not staged:
        raise SystemExit("pass at least one --archive, --native-library, or --include-current-native")
    return staged


def copy_native(stage: Path, rid: str, native: Path) -> None:
    if not native.is_file():
        raise FileNotFoundError(native)
    destination = stage / "runtimes" / rid / "native" / native_name_for_rid(rid)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(native, destination)
    print(f"Staged {rid}: {destination.relative_to(stage)}")


def copy_package_source(stage: Path, version: str) -> None:
    ignore = shutil.ignore_patterns("node_modules", "tests", "src", "*.tgz", ".DS_Store")
    shutil.copytree(PACKAGE, stage, ignore=ignore)

    package_json = json.loads((stage / "package.json").read_text(encoding="utf-8"))
    package_json["version"] = version
    (stage / "package.json").write_text(json.dumps(package_json, indent=2) + "\n", encoding="utf-8")

    docs = stage / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    for relative in [
        "docs/typescript_binding.md",
        "docs/bindings.md",
        "docs/contracts.md",
        "docs/binary_schema.md",
        "docs/output_formats.md",
        "docs/language_extensions.md",
        "docs/tree_sitter_queries.md",
        "docs/encoding.md",
    ]:
        source = ROOT / relative
        if source.is_file():
            shutil.copy2(source, docs / source.name)

    examples = stage / "examples"
    examples.mkdir(parents=True, exist_ok=True)
    example_source = ROOT / "examples" / "typescript" / "01_parse_java"
    if example_source.is_dir():
        shutil.copytree(example_source, examples / "01_parse_java", ignore=shutil.ignore_patterns("node_modules"))

    for name in ["AI_AGENT_GUIDE.md", "NOTICE", "THIRD_PARTY_NOTICES.md"]:
        source = ROOT / name
        if source.is_file():
            shutil.copy2(source, stage / name)


def run_build() -> None:
    subprocess.run(["npm", "install"], cwd=PACKAGE, check=True)
    subprocess.run(["npm", "run", "build"], cwd=PACKAGE, check=True)


def npm_pack(stage: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        ["npm", "pack", "--json", "--pack-destination", str(output_dir)],
        cwd=stage,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    payload = json.loads(completed.stdout)
    filename = payload[0]["filename"]
    package = output_dir / filename
    if not package.is_file():
        raise AssertionError(f"npm package was not created: {package}")
    return package


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    run_build()

    with tempfile.TemporaryDirectory(prefix="fastparse-npm-stage-") as temp:
        stage = Path(temp) / "package"
        copy_package_source(stage, args.version)
        staged = stage_native_assets(stage, args)
        package = npm_pack(stage, output_dir)

    print(f"npm package: {package}")
    print(f"native RIDs: {', '.join(sorted(staged))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
