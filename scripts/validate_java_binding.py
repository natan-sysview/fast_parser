#!/usr/bin/env python3
"""Validate the local FastParse Java binding without publishing."""
from __future__ import annotations

import platform
import shutil
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASSES = Path("/tmp/fastparse-java-classes")


def core_name() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "libfastparse.dylib"
    if system == "windows":
        return "fastparse.dll"
    return "libfastparse.so"


def jni_name() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "libfastparse_jni.dylib"
    if system == "windows":
        return "fastparse_jni.dll"
    return "libfastparse_jni.so"


def java_sources() -> list[str]:
    sources = [str(p) for p in (ROOT / "bindings/java/fastparse/src/main/java").rglob("*.java")]
    sources += [str(ROOT / "bindings/java/fastparse/src/test/java/dev/fastparse/FastParseSmoke.java")]
    return sources


def main() -> int:
    subprocess.run([sys.executable, "scripts/build_java_jni.py"], check=True, cwd=str(ROOT))
    if CLASSES.exists():
        shutil.rmtree(CLASSES)
    CLASSES.mkdir(parents=True)
    subprocess.run(["javac", "--release", "8", "-d", str(CLASSES)] + java_sources(), check=True, cwd=str(ROOT))
    core = ROOT / "bin" / core_name()
    jni = ROOT / "bin" / jni_name()
    subprocess.run(["java", "-cp", str(CLASSES), "dev.fastparse.FastParseSmoke", str(core), str(jni)], check=True, cwd=str(ROOT))
    print("FastParse Java binding validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
