#!/usr/bin/env python3
"""Package a FastParse language extension native archive."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package a FastParse language extension.")
    parser.add_argument("--language", required=True)
    parser.add_argument("--version", default="0.1.0-preview.1")
    parser.add_argument("--platform", default=default_platform())
    parser.add_argument("--arch", default=default_arch())
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build-language-extension")
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist" / "languages")
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


def rid_for(platform_name: str, arch: str) -> str:
    prefix = {"linux": "linux", "macos": "osx", "windows": "win"}[platform_name]
    return f"{prefix}-{arch}"


def library_name(language: str, platform_name: str) -> str:
    native = native_language_name(language)
    if platform_name == "windows":
        return f"fastparse_language_{native}.dll"
    if platform_name == "macos":
        return f"libfastparse_language_{native}.dylib"
    return f"libfastparse_language_{native}.so"


def target_name(language: str) -> str:
    return f"fastparse_language_{native_language_name(language)}"


def native_language_name(language: str) -> str:
    return language.strip().lower().replace("-", "_")


def cmake_language_key(language: str) -> str:
    return native_language_name(language).upper()


def grammar_dir(language: str) -> Path:
    return ROOT / "grammars" / f"tree-sitter-{language}"


def build_extension(language: str, build_dir: Path) -> None:
    grammar = grammar_dir(language)
    if not (grammar / "src" / "parser.c").is_file():
        raise FileNotFoundError(f"grammar is not vendored: {grammar}")
    cmake_var = f"FASTPARSE_{cmake_language_key(language)}_GRAMMAR_DIR={grammar}"
    subprocess.run(
        ["cmake", "-S", str(ROOT), "-B", str(build_dir), "-DCMAKE_BUILD_TYPE=Release", f"-D{cmake_var}"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        ["cmake", "--build", str(build_dir), "--config", "Release", "--target", target_name(language)],
        cwd=ROOT,
        check=True,
    )


def copy_tree_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def package_extension(args: argparse.Namespace) -> Path:
    language = args.language
    platform_name = args.platform.lower()
    arch = args.arch.lower()
    rid = rid_for(platform_name, arch)
    native_name = library_name(language, platform_name)
    built_library = ROOT / "bin" / native_name
    if not built_library.is_file():
        raise FileNotFoundError(f"built extension library not found: {built_library}")

    package_name = f"fastparse-language-{language}-{args.version}-{platform_name}-{arch}"
    package_dir = args.dist_dir.resolve() / package_name
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    native_dir = package_dir / "native" / rid
    native_dir.mkdir(parents=True)
    shutil.copy2(built_library, native_dir / native_name)

    extension_dir = ROOT / "extensions" / language
    shutil.copy2(extension_dir / "manifest.json", package_dir / "manifest.json")
    shutil.copy2(extension_dir / "README.md", package_dir / "README.md")
    copy_tree_if_exists(extension_dir / "queries", package_dir / "queries")

    grammar = grammar_dir(language)
    grammar_meta = package_dir / "grammar"
    grammar_meta.mkdir()
    for name in ["LICENSE", "README.md", "tree-sitter.json", "package.json"]:
        source = grammar / name
        if source.exists():
            shutil.copy2(source, grammar_meta / name)

    manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest["version"] = args.version
    manifest["platforms"] = [rid]
    (package_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if platform_name == "windows":
        archive = args.dist_dir.resolve() / f"{package_name}.zip"
        if archive.exists():
            archive.unlink()
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in package_dir.rglob("*"):
                zf.write(path, path.relative_to(package_dir.parent))
    else:
        archive = args.dist_dir.resolve() / f"{package_name}.tar.gz"
        if archive.exists():
            archive.unlink()
        with tarfile.open(archive, "w:gz") as tf:
            tf.add(package_dir, arcname=package_dir.name)
    return archive


def main() -> int:
    args = parse_args()
    if not args.skip_build:
        build_extension(args.language, args.build_dir.resolve())
    archive = package_extension(args)
    print(f"Language extension archive: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
