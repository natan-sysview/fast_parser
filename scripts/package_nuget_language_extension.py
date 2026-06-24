#!/usr/bin/env python3
"""Build a NuGet package for a FastParse language extension."""

from __future__ import annotations

import argparse
import re
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_RE = re.compile(
    r"^fastparse-language-(?P<language>[a-z0-9_-]+)-(?P<version>.+)-(?P<platform>linux|macos|windows)-(?P<arch>x64|arm64)\.(?P<ext>tar\.gz|zip)$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build FastParser.Language.<Name>.nupkg.")
    parser.add_argument("--language", required=True, choices=["python"])
    parser.add_argument("--version", required=True)
    parser.add_argument("--archive", action="append", type=Path, default=[])
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "nuget-languages")
    return parser.parse_args()


def package_id(language: str) -> str:
    return "FastParser.Language." + "".join(part.capitalize() for part in language.replace("-", "_").split("_"))


def rid_for(platform_name: str, arch: str) -> str:
    return {"linux": "linux", "macos": "osx", "windows": "win"}[platform_name] + f"-{arch}"


def native_name(language: str, platform_name: str) -> str:
    if platform_name == "windows":
        return f"fastparse_language_{language}.dll"
    if platform_name == "macos":
        return f"libfastparse_language_{language}.dylib"
    return f"libfastparse_language_{language}.so"


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
        raise ValueError(f"unsupported archive: {archive}")
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise AssertionError(f"expected one package root in {archive}, found {len(roots)}")
    return roots[0]


def stage_archive(language: str, archive: Path, staging: Path) -> str:
    match = ARCHIVE_RE.match(archive.name)
    if not match:
        raise AssertionError(f"unexpected language archive name: {archive.name}")
    if match.group("language") != language:
        raise AssertionError(f"archive language mismatch: {archive.name}")

    platform_name = match.group("platform")
    arch = match.group("arch")
    rid = rid_for(platform_name, arch)
    expected_native = native_name(language, platform_name)

    with tempfile.TemporaryDirectory(prefix="fastparse-language-nuget-") as temp:
        root = extract_archive(archive, Path(temp))
        native = root / "native" / rid / expected_native
        if not native.is_file():
            raise AssertionError(f"missing {native}")
        destination = staging / "runtimes" / rid / "native" / expected_native
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(native, destination)

        manifest = root / "manifest.json"
        if manifest.is_file():
            manifest_target = staging / "contentFiles" / "any" / "any" / "fastparse" / "languages" / language / "manifest.json"
            manifest_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(manifest, manifest_target)

        readme = root / "README.md"
        if readme.is_file():
            shutil.copy2(readme, staging / "README.md")
    return rid


def write_targets(language: str, staging: Path) -> None:
    targets_dir = staging / "buildTransitive"
    targets_dir.mkdir(parents=True, exist_ok=True)
    targets = f'''<Project>
  <Target Name="FastParserLanguage{language.capitalize()}CopyManifest" AfterTargets="Build">
    <ItemGroup>
      <FastParserLanguageManifest Include="$(MSBuildThisFileDirectory)..\\contentFiles\\any\\any\\fastparse\\languages\\{language}\\manifest.json" />
    </ItemGroup>
    <Copy SourceFiles="@(FastParserLanguageManifest)"
          DestinationFolder="$(OutDir)fastparse\\languages\\{language}\\"
          SkipUnchangedFiles="true"
          Condition="Exists('%(FastParserLanguageManifest.Identity)')" />
  </Target>
</Project>
'''
    (targets_dir / f"{package_id(language)}.targets").write_text(targets, encoding="utf-8")


def write_nuspec(language: str, version: str, staging: Path) -> Path:
    pid = package_id(language)
    readme = staging / "README.md"
    if not readme.exists():
        readme.write_text(f"# {pid}\n\nFastParse {language} language extension.\n", encoding="utf-8")
    nuspec = staging / f"{pid}.nuspec"
    nuspec.write_text(
        f'''<?xml version="1.0" encoding="utf-8"?>
<package>
  <metadata>
    <id>{escape(pid)}</id>
    <version>{escape(version)}</version>
    <authors>natan-sysview</authors>
    <description>FastParse {escape(language)} language extension native assets.</description>
    <packageTypes>
      <packageType name="Dependency" />
    </packageTypes>
    <license type="expression">Apache-2.0</license>
    <projectUrl>https://github.com/natan-sysview/fast_parser</projectUrl>
    <repository type="git" url="https://github.com/natan-sysview/fast_parser" />
    <tags>fastparse tree-sitter parser {escape(language)} native</tags>
    <readme>README.md</readme>
    <dependencies>
      <group targetFramework="net8.0">
        <dependency id="FastParser" version="{escape(version)}" />
      </group>
      <group targetFramework="net9.0">
        <dependency id="FastParser" version="{escape(version)}" />
      </group>
    </dependencies>
    <contentFiles>
      <files include="any/any/fastparse/languages/{escape(language)}/manifest.json" buildAction="None" copyToOutput="true" />
    </contentFiles>
  </metadata>
</package>
''',
        encoding="utf-8",
    )
    return nuspec


def make_package(staging: Path, nuspec: Path, output_dir: Path, package_name: str, version: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    package = output_dir / f"{package_name}.{version}.nupkg"
    if package.exists():
        package.unlink()
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(nuspec, nuspec.name)
        for path in sorted(staging.rglob("*")):
            if path.is_file() and path != nuspec:
                zf.write(path, path.relative_to(staging))
    return package


def main() -> int:
    args = parse_args()
    if not args.archive:
        raise SystemExit("pass at least one --archive")
    with tempfile.TemporaryDirectory(prefix="fastparse-language-nuget-stage-") as temp:
        staging = Path(temp)
        seen = {stage_archive(args.language, archive.resolve(), staging) for archive in args.archive}
        required = {"linux-x64", "osx-arm64", "osx-x64", "win-x64"}
        missing = sorted(required - seen)
        if missing:
            raise AssertionError(f"missing required RID assets: {', '.join(missing)}")
        write_targets(args.language, staging)
        nuspec = write_nuspec(args.language, args.version, staging)
        package = make_package(staging, nuspec, args.output_dir.resolve(), package_id(args.language), args.version)
    print(f"NuGet language package: {package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
