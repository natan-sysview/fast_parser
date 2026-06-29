#!/usr/bin/env python3
"""Build a NuGet package for a FastParse language extension."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
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
    parser.add_argument("--language", required=True, choices=["python", "rust"])
    parser.add_argument("--version", required=True)
    parser.add_argument("--archive", action="append", type=Path, default=[])
    parser.add_argument("--dependency-source", type=Path, help="Optional local NuGet source used to restore FastParser while packing.")
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


def write_pack_project(language: str, version: str, staging: Path) -> Path:
    pid = package_id(language)
    readme = staging / "README.md"
    if not readme.exists():
        readme.write_text(f"# {pid}\n\nFastParse {language} language extension.\n", encoding="utf-8")
    project = staging / f"{pid}.csproj"
    project.write_text(
        f'''<?xml version="1.0" encoding="utf-8"?>
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFrameworks>net8.0;net9.0</TargetFrameworks>
    <PackageId>{escape(pid)}</PackageId>
    <Version>{escape(version)}</Version>
    <Authors>natan-sysview</Authors>
    <Company>natan-sysview</Company>
    <Description>FastParse {escape(language)} language extension native assets.</Description>
    <PackageTags>fastparse;tree-sitter;parser;{escape(language)};native</PackageTags>
    <PackageProjectUrl>https://github.com/natan-sysview/fast_parser</PackageProjectUrl>
    <RepositoryUrl>https://github.com/natan-sysview/fast_parser</RepositoryUrl>
    <RepositoryType>git</RepositoryType>
    <PackageLicenseExpression>Apache-2.0</PackageLicenseExpression>
    <PackageReadmeFile>README.md</PackageReadmeFile>
    <PackageRequireLicenseAcceptance>false</PackageRequireLicenseAcceptance>
    <PackageReleaseNotes>Preview FastParse language extension for {escape(language)}.</PackageReleaseNotes>
    <PackageType>Dependency</PackageType>
    <IncludeBuildOutput>false</IncludeBuildOutput>
    <SuppressDependenciesWhenPacking>false</SuppressDependenciesWhenPacking>
    <NoWarn>$(NoWarn);NU5128</NoWarn>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="FastParser" Version="{escape(version)}" />
  </ItemGroup>

  <ItemGroup>
    <None Include="README.md" Pack="true" PackagePath="/" />
    <None Include="buildTransitive/{escape(pid)}.targets" Pack="true" PackagePath="buildTransitive/" />
    <None Include="runtimes/**" Pack="true" PackagePath="runtimes/%(RecursiveDir)%(Filename)%(Extension)" />
    <Content Include="contentFiles/any/any/fastparse/languages/{escape(language)}/manifest.json"
             Pack="true"
             PackagePath="contentFiles/any/any/fastparse/languages/{escape(language)}/manifest.json"
             PackageBuildAction="None"
             PackageCopyToOutput="true" />
  </ItemGroup>
</Project>
''',
        encoding="utf-8",
    )
    return project


def make_package(
    staging: Path,
    project: Path,
    output_dir: Path,
    package_name: str,
    version: str,
    dependency_source: Path | None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    package = output_dir / f"{package_name}.{version}.nupkg"
    if package.exists():
        package.unlink()
    command = [
        "dotnet",
        "pack",
        str(project),
        "--configuration",
        "Release",
        "--output",
        str(output_dir),
        f"-p:PackageVersion={version}",
    ]
    if dependency_source is not None:
        command.extend(["--source", str(dependency_source)])
    subprocess.run(
        command,
        cwd=staging,
        check=True,
    )
    if not package.is_file():
        raise AssertionError(f"expected NuGet package was not created: {package}")
    return package


def validate_package(package: Path, language: str) -> None:
    pid = package_id(language)
    required = {
        "[Content_Types].xml",
        "_rels/.rels",
        f"{pid}.nuspec",
        "README.md",
        f"buildTransitive/{pid}.targets",
        f"contentFiles/any/any/fastparse/languages/{language}/manifest.json",
        f"runtimes/linux-x64/native/{native_name(language, 'linux')}",
        f"runtimes/osx-arm64/native/{native_name(language, 'macos')}",
        f"runtimes/osx-x64/native/{native_name(language, 'macos')}",
        f"runtimes/win-x64/native/{native_name(language, 'windows')}",
    }
    with zipfile.ZipFile(package) as zf:
        names = set(zf.namelist())
    missing = sorted(required - names)
    if missing:
        raise AssertionError(f"NuGet language package missing entries: {', '.join(missing)}")


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
        project = write_pack_project(args.language, args.version, staging)
        package = make_package(
            staging,
            project,
            args.output_dir.resolve(),
            package_id(args.language),
            args.version,
            args.dependency_source.resolve() if args.dependency_source else None,
        )
        validate_package(package, args.language)
    print(f"NuGet language package: {package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
