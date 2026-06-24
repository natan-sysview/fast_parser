#!/usr/bin/env python3
"""Build a FastParse Python wheel with the native runtime bundled."""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PACKAGE = ROOT / "bindings" / "python"


def default_platform_tag() -> str:
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Darwin":
        if machine in {"arm64", "aarch64"}:
            return "macosx_11_0_arm64"
        return "macosx_10_15_x86_64"
    if system == "Windows":
        return "win_amd64" if machine in {"amd64", "x86_64"} else f"win_{machine}"
    if machine in {"x86_64", "amd64"}:
        return "manylinux2014_x86_64"
    if machine in {"aarch64", "arm64"}:
        return "manylinux2014_aarch64"
    return f"linux_{machine}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build FastParse Python wheel.")
    parser.add_argument("--version", required=True, help="Release version, for example 0.1.0-preview.15")
    parser.add_argument("--platform-tag", default=default_platform_tag())
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "python")
    return parser.parse_args()


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def venv_bin(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts"
    return venv_dir / "bin"


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    build_dir = PYTHON_PACKAGE / "build"
    egg_info = PYTHON_PACKAGE / "fastparse.egg-info"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if egg_info.exists():
        shutil.rmtree(egg_info)

    env = os.environ.copy()
    env["FASTPARSE_PY_VERSION"] = args.version
    env["FASTPARSE_PY_PLATFORM_TAG"] = args.platform_tag

    with tempfile.TemporaryDirectory(prefix="fastparse-wheel-build-") as temp:
        venv_dir = Path(temp) / "venv"
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        python = venv_python(venv_dir)
        subprocess.run(
            [str(python), "-m", "pip", "install", "--upgrade", "setuptools>=61", "wheel", "cmake>=3.20"],
            check=True,
        )
        env["PATH"] = str(venv_bin(venv_dir)) + os.pathsep + env.get("PATH", "")
        subprocess.run(
            [
                str(python),
                "setup.py",
                "bdist_wheel",
                "--dist-dir",
                str(output_dir),
                "--plat-name",
                args.platform_tag,
            ],
            cwd=PYTHON_PACKAGE,
            env=env,
            check=True,
        )

    wheels = sorted(output_dir.glob("fastparse-*.whl"), key=lambda path: path.stat().st_mtime)
    if not wheels:
        raise AssertionError(f"no Python wheel created under {output_dir}")
    print(f"Python wheel: {wheels[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
