#!/usr/bin/env python3
"""Build the FastParse Java JNI bridge for the current platform."""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rid() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "darwin":
        os_part = "macos"
    elif system == "windows":
        os_part = "windows"
    else:
        os_part = "linux"
    if machine in {"x86_64", "amd64"}:
        arch = "x64"
    elif machine in {"arm64", "aarch64"}:
        arch = "arm64"
    else:
        arch = machine
    return f"{os_part}-{arch}"


def jni_name() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "libfastparse_jni.dylib"
    if system == "windows":
        return "fastparse_jni.dll"
    return "libfastparse_jni.so"


def core_name() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "libfastparse.dylib"
    if system == "windows":
        return "fastparse.dll"
    return "libfastparse.so"


def java_home() -> Path:
    env = os.environ.get("JAVA_HOME")
    if env:
        return Path(env)
    if platform.system().lower() == "darwin":
        value = subprocess.check_output(["/usr/libexec/java_home"], text=True).strip()
        return Path(value)
    raise SystemExit("JAVA_HOME is required to build the FastParse JNI bridge")


def build(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    source = ROOT / "bindings/java/fastparse/src/main/c/fastparse_jni.c"
    out = output_dir / jni_name()
    home = java_home()
    include = home / "include"
    system = platform.system().lower()
    if system == "windows":
        win_include = include / "win32"
        cl = shutil.which("cl")
        if not cl:
            raise SystemExit("MSVC cl.exe is required on Windows. Run from a Developer Command Prompt.")
        subprocess.run([
            "cl", "/nologo", "/LD", f"/I{include}", f"/I{win_include}", f"/I{ROOT / 'include'}",
            str(source), f"/Fe:{out}"
        ], check=True, cwd=str(ROOT))
    else:
        platform_include = include / ("darwin" if system == "darwin" else "linux")
        cc = os.environ.get("CC", "cc")
        command = [
            cc, "-shared", "-fPIC", f"-I{include}", f"-I{platform_include}", f"-I{ROOT / 'include'}",
            "-o", str(out), str(source)
        ]
        if system == "linux":
            command.append("-ldl")
        subprocess.run(command, check=True, cwd=str(ROOT))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(ROOT / "bin"))
    parser.add_argument("--copy-resources", action="store_true", help="Copy core and JNI native libraries into Java resource layout for local Maven packaging")
    args = parser.parse_args()
    output = build(Path(args.output_dir).resolve())
    print(f"Built JNI bridge: {output}")
    if args.copy_resources:
        resource_dir = ROOT / "bindings/java/fastparse/src/main/resources/dev/fastparse/native" / rid()
        resource_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, resource_dir / output.name)
        core = ROOT / "bin" / core_name()
        if core.exists():
            shutil.copy2(core, resource_dir / core.name)
            print(f"Copied core native library: {resource_dir / core.name}")
        else:
            print(f"Core native library not found, skipped: {core}")
        print(f"Copied JNI resource: {resource_dir / output.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
