#!/usr/bin/env python3
"""Build a PyPI wheel for a FastParse language extension."""

from __future__ import annotations

import argparse
import platform
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build fastparse-language-<language> wheel.")
    parser.add_argument("--language", required=True)
    parser.add_argument("--version", default="0.1.0-preview.1")
    parser.add_argument("--platform-tag", default=default_platform_tag())
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "python-languages")
    parser.add_argument("--skip-build", action="store_true")
    return parser.parse_args()


def default_platform_tag() -> str:
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Darwin":
        return "macosx_11_0_arm64" if machine in {"arm64", "aarch64"} else "macosx_10_15_x86_64"
    if system == "Windows":
        return "win_amd64" if machine in {"amd64", "x86_64"} else f"win_{machine}"
    return "manylinux2014_x86_64" if machine in {"x86_64", "amd64"} else f"manylinux2014_{machine}"


def pep440(version: str) -> str:
    if "-preview." in version:
        base, preview = version.split("-preview.", 1)
        return f"{base}rc{preview}"
    return version


def platform_key() -> str:
    system = platform.system()
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        arch = "x64"
    elif machine in {"arm64", "aarch64"}:
        arch = "arm64"
    else:
        arch = machine
    if system == "Darwin":
        return f"osx-{arch}"
    if system == "Windows":
        return f"win-{arch}"
    return f"linux-{arch}"


def native_name(language: str) -> str:
    native = native_language_name(language)
    if platform.system() == "Windows":
        return f"fastparse_language_{native}.dll"
    if platform.system() == "Darwin":
        return f"libfastparse_language_{native}.dylib"
    return f"libfastparse_language_{native}.so"


def native_language_name(language: str) -> str:
    return language.strip().lower().replace("-", "_")


def build_native(language: str, version: str) -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/package_language_extension.py",
            "--language",
            language,
            "--version",
            version,
        ],
        cwd=ROOT,
        check=True,
    )


def write_project(temp: Path, language: str, version: str, platform_tag: str) -> None:
    native_language = native_language_name(language)
    package_name = f"fastparse_language_{native_language}"
    package_dir = temp / package_name
    native_dir = package_dir / "native" / platform_key()
    native_dir.mkdir(parents=True)
    (package_dir / "native" / "__init__.py").write_text("", encoding="utf-8")

    source_native = ROOT / "bin" / native_name(language)
    if not source_native.is_file():
        raise FileNotFoundError(source_native)
    shutil.copy2(source_native, native_dir / source_native.name)
    manifest_path = package_dir / "manifest.json"
    shutil.copy2(ROOT / "extensions" / language / "manifest.json", manifest_path)
    query_package = package_dir / "queries"
    query_package.mkdir()
    (query_package / "__init__.py").write_text("", encoding="utf-8")
    queries_source = ROOT / "extensions" / language / "queries"
    if queries_source.is_dir():
        shutil.copytree(queries_source, query_package, dirs_exist_ok=True)
        (query_package / "__init__.py").write_text("", encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = version
    manifest["platforms"] = [platform_key()]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (package_dir / "py.typed").write_text("", encoding="utf-8")
    (package_dir / "__init__.py").write_text(
        f'''from __future__ import annotations

import platform
from importlib import resources
from pathlib import Path

__version__ = "{pep440(version)}"
LANGUAGE = "{language}"
NATIVE_LANGUAGE = "{native_language}"


def _platform_key() -> str:
    machine = platform.machine().lower()
    if machine in {{"x86_64", "amd64"}}:
        arch = "x64"
    elif machine in {{"arm64", "aarch64"}}:
        arch = "arm64"
    else:
        arch = machine

    system = platform.system()
    if system == "Darwin":
        return f"osx-{{arch}}"
    if system == "Windows":
        return f"win-{{arch}}"
    return f"linux-{{arch}}"


def extension_path() -> Path:
    if platform.system() == "Windows":
        filename = "fastparse_language_{native_language}.dll"
    elif platform.system() == "Darwin":
        filename = "libfastparse_language_{native_language}.dylib"
    else:
        filename = "libfastparse_language_{native_language}.so"
    path = resources.files(__package__) / "native" / _platform_key() / filename
    return Path(str(path))


def query_path(name: str = "frameworks") -> Path:
    path = resources.files(__package__) / "queries" / f"{{name}}.scm"
    return Path(str(path))
''',
        encoding="utf-8",
    )
    (temp / "README.md").write_text(
        f"# fastparse-language-{language}\n\nFastParse {language} language extension wheel.\n",
        encoding="utf-8",
    )
    (temp / "setup.py").write_text(
        f'''from setuptools import setup
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        super().finalize_options()
        self.root_is_pure = False
        self.plat_name = "{platform_tag}" or self.plat_name

    def get_tag(self):
        _python, _abi, platform_tag = super().get_tag()
        return "py3", "none", "{platform_tag}" or platform_tag


setup(
    name="fastparse-language-{language}",
    version="{pep440(version)}",
    description="FastParse {language} language extension",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    install_requires=["fastparse=={pep440(version)}"],
    packages=["{package_name}", "{package_name}.native", "{package_name}.queries"],
    package_data={{{package_name!r}: ["manifest.json", "py.typed", "native/*/*", "queries/*.scm"]}},
    include_package_data=True,
    zip_safe=False,
    cmdclass={{"bdist_wheel": bdist_wheel}},
)
''',
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    if not args.skip_build:
        build_native(args.language, args.version)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"fastparse-language-{args.language}-wheel-") as temp_raw:
        temp = Path(temp_raw)
        venv = temp / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        python = venv / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")
        subprocess.run([str(python), "-m", "pip", "install", "setuptools>=61", "wheel"], check=True)
        write_project(temp, args.language, args.version, args.platform_tag)
        subprocess.run(
            [str(python), "setup.py", "bdist_wheel", "--dist-dir", str(args.output_dir.resolve())],
            cwd=temp,
            check=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
