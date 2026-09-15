#!/usr/bin/env python3
"""Build and archive the Java JNI bridge for one platform/arch."""
from __future__ import annotations

import argparse
import platform
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def default_platform() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    if system == "windows":
        return "windows"
    return "linux"


def default_arch() -> str:
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        return "x64"
    if machine in {"arm64", "aarch64"}:
        return "arm64"
    return machine


def jni_name(platform_name: str) -> str:
    if platform_name == "windows":
        return "fastparse_jni.dll"
    if platform_name == "macos":
        return "libfastparse_jni.dylib"
    return "libfastparse_jni.so"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a FastParse Java JNI platform archive.")
    parser.add_argument("--version", required=True)
    parser.add_argument("--platform", default=default_platform(), choices=["linux", "macos", "windows"])
    parser.add_argument("--arch", default=default_arch(), choices=["x64", "arm64"])
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist/java-jni")
    args = parser.parse_args()

    subprocess.run([sys.executable, "scripts/build_java_jni.py"], cwd=str(ROOT), check=True)
    args.dist_dir.mkdir(parents=True, exist_ok=True)
    lib = ROOT / "bin" / jni_name(args.platform)
    if not lib.is_file():
        raise FileNotFoundError(lib)

    base = f"fastparse-java-jni-{args.version}-{args.platform}-{args.arch}"
    if args.platform == "windows":
        archive = args.dist_dir / f"{base}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(lib, lib.name)
    else:
        archive = args.dist_dir / f"{base}.tar.gz"
        with tarfile.open(archive, "w:gz") as tf:
            tf.add(lib, arcname=lib.name)
    print(f"Java JNI archive: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
