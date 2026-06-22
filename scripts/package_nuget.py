#!/usr/bin/env python3
"""Build the FastParse NuGet package from native release archives."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "bindings" / "csharp" / "FastParse" / "FastParse.csproj"
ARCHIVE_RE = re.compile(r"^fastparse-(?P<version>.+)-(?P<platform>linux|macos|windows)-(?P<arch>x64|arm64)\.(?P<ext>tar\.gz|zip)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build FastParser.nupkg with RID-specific native libraries.")
    parser.add_argument("--version", required=True, help="NuGet package version, for example 0.1.0-preview")
    parser.add_argument("--archive", action="append", type=Path, default=[], help="FastParse release archive. May be passed multiple times.")
    parser.add_argument("--release-tag", help="Download native archives from a GitHub release tag before packing.")
    parser.add_argument("--repository", default="natan-sysview/fast_parser", help="GitHub repository used with --release-tag.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "nuget")
    return parser.parse_args()


def download_release_archives(repository: str, tag: str, destination: Path) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    url = f"https://api.github.com/repos/{repository}/releases/tags/{tag}"
    with urllib.request.urlopen(url) as response:
        release = json.load(response)

    archives: list[Path] = []
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        if not ARCHIVE_RE.match(name):
            continue
        target = destination / name
        print(f"Downloading {name}...", flush=True)
        urllib.request.urlretrieve(asset["browser_download_url"], target)
        archives.append(target)

    if not archives:
        raise AssertionError(f"no native FastParse archives found in release {repository}@{tag}")
    return archives


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


def rid_for(platform_name: str, arch: str) -> str:
    prefix = {
        "linux": "linux",
        "macos": "osx",
        "windows": "win",
    }[platform_name]
    return f"{prefix}-{arch}"


def native_file_for(platform_name: str) -> tuple[Path, str]:
    if platform_name == "windows":
        return Path("bin") / "fastparse.dll", "fastparse.dll"
    if platform_name == "macos":
        return Path("lib") / "libfastparse.dylib", "libfastparse.dylib"
    return Path("lib") / "libfastparse.so", "libfastparse.so"


def stage_native_assets(archives: list[Path], native_root: Path) -> None:
    runtimes = native_root / "runtimes"
    if runtimes.exists():
        shutil.rmtree(runtimes)
    seen: set[str] = set()

    for archive in archives:
        match = ARCHIVE_RE.match(archive.name)
        if not match:
            raise AssertionError(f"archive does not match FastParse release naming: {archive.name}")

        platform_name = match.group("platform")
        arch = match.group("arch")
        rid = rid_for(platform_name, arch)
        source_relative, native_name = native_file_for(platform_name)

        with tempfile.TemporaryDirectory(prefix="fastparse-nuget-") as temp:
            package_root = extract_archive(archive, Path(temp))
            source = package_root / source_relative
            if not source.is_file():
                raise AssertionError(f"missing native library {source_relative} in {archive}")

            destination = runtimes / rid / "native" / native_name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            seen.add(rid)
            print(f"Staged {rid}: {destination.relative_to(native_root)}")

    required = {"linux-x64", "osx-arm64", "osx-x64", "win-x64"}
    missing = sorted(required - seen)
    if missing:
        raise AssertionError(f"missing required native RID assets: {', '.join(missing)}")


def build_package(version: str, native_root: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "dotnet",
            "pack",
            str(PROJECT),
            "--configuration",
            "Release",
            "--output",
            str(output_dir),
            f"-p:PackageVersion={version}",
            f"-p:NativeAssetsRoot={native_root}",
        ],
        cwd=ROOT,
        check=True,
    )

    package = output_dir / f"FastParser.{version}.nupkg"
    if not package.is_file():
        raise AssertionError(f"expected NuGet package was not created: {package}")
    return package


def validate_package(package: Path) -> None:
    required = {
        "lib/net9.0/FastParse.dll",
        "runtimes/linux-x64/native/libfastparse.so",
        "runtimes/osx-arm64/native/libfastparse.dylib",
        "runtimes/osx-x64/native/libfastparse.dylib",
        "runtimes/win-x64/native/fastparse.dll",
        "README.md",
    }
    with zipfile.ZipFile(package) as zf:
        names = set(zf.namelist())
    missing = sorted(required - names)
    if missing:
        raise AssertionError(f"NuGet package missing entries: {', '.join(missing)}")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    archives = [path.resolve() for path in args.archive]

    if args.release_tag:
        archives.extend(download_release_archives(args.repository, args.release_tag, output_dir / "assets"))
    if not archives:
        raise SystemExit("pass at least one --archive or use --release-tag")

    native_root = output_dir / "native"
    stage_native_assets(archives, native_root)
    package = build_package(args.version, native_root, output_dir)
    validate_package(package)

    print(f"NuGet package: {package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
