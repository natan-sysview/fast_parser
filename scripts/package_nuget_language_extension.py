#!/usr/bin/env python3
"""Build a NuGet package for a FastParse language extension."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import tarfile
import tempfile
import uuid
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_RE = re.compile(
    r"^fastparse-language-(?P<language>[a-z0-9_-]+)-(?P<version>.+)-(?P<platform>linux|macos|windows)-(?P<arch>x64|arm64)\.(?P<ext>tar\.gz|zip)$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build FastParser.Language.<Name>.nupkg.")
    parser.add_argument("--language", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--core-version")
    parser.add_argument("--archive", action="append", type=Path, default=[])
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "nuget-languages")
    parser.add_argument("--require-all-rids", action="store_true")
    return parser.parse_args()


def package_id(language: str) -> str:
    if native_language_name(language) == "javaswing":
        return "FastParser.Language.JavaSwing"
    return "FastParser.Language." + "".join(part.capitalize() for part in language.replace("-", "_").split("_"))


def native_language_name(language: str) -> str:
    return language.strip().lower().replace("-", "_")


def rid_for(platform_name: str, arch: str) -> str:
    return {"linux": "linux", "macos": "osx", "windows": "win"}[platform_name] + f"-{arch}"


def native_name(language: str, platform_name: str) -> str:
    native = native_language_name(language)
    if platform_name == "windows":
        return f"fastparse_language_{native}.dll"
    if platform_name == "macos":
        return f"libfastparse_language_{native}.dylib"
    return f"libfastparse_language_{native}.so"


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

        queries = root / "queries"
        if queries.is_dir():
            query_target = staging / "contentFiles" / "any" / "any" / "fastparse" / "languages" / language / "queries"
            shutil.copytree(queries, query_target, dirs_exist_ok=True)

        readme = root / "README.md"
        if readme.is_file():
            shutil.copy2(readme, staging / "README.md")
    return rid


def write_targets(language: str, staging: Path) -> None:
    targets_dir = staging / "buildTransitive"
    targets_dir.mkdir(parents=True, exist_ok=True)
    target_name = "".join(part.capitalize() for part in language.replace("-", "_").split("_"))
    targets = f'''<Project>
  <Target Name="FastParserLanguage{target_name}CopyManifest" AfterTargets="Build">
    <ItemGroup>
      <FastParserLanguageManifest Include="$(MSBuildThisFileDirectory)..\\contentFiles\\any\\any\\fastparse\\languages\\{language}\\manifest.json" />
      <FastParserLanguageQueries Include="$(MSBuildThisFileDirectory)..\\contentFiles\\any\\any\\fastparse\\languages\\{language}\\queries\\**\\*" />
    </ItemGroup>
    <Copy SourceFiles="@(FastParserLanguageManifest)"
          DestinationFolder="$(OutDir)fastparse\\languages\\{language}\\"
          SkipUnchangedFiles="true"
          Condition="Exists('%(FastParserLanguageManifest.Identity)')" />
    <Copy SourceFiles="@(FastParserLanguageQueries)"
          DestinationFiles="@(FastParserLanguageQueries->'$(OutDir)fastparse\\languages\\{language}\\queries\\%(RecursiveDir)%(Filename)%(Extension)')"
          SkipUnchangedFiles="true" />
  </Target>
</Project>
'''
    (targets_dir / f"{package_id(language)}.targets").write_text(targets, encoding="utf-8")


def write_nuspec(language: str, version: str, core_version: str, staging: Path) -> Path:
    pid = package_id(language)
    readme = staging / "README.md"
    if not readme.exists():
        readme.write_text(f"# {pid}\n\nFastParse {language} language extension.\n", encoding="utf-8")
    nuspec = staging / f"{pid}.nuspec"
    nuspec.write_text(
        f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
  <metadata>
    <id>{escape(pid)}</id>
    <version>{escape(version)}</version>
    <authors>natan-sysview</authors>
    <description>FastParse {escape(language)} language extension native assets.</description>
    <releaseNotes>Preview FastParse language extension for {escape(language)}.</releaseNotes>
    <packageTypes>
      <packageType name="Dependency" />
    </packageTypes>
    <license type="expression">Apache-2.0</license>
    <licenseUrl>https://licenses.nuget.org/Apache-2.0</licenseUrl>
    <projectUrl>https://github.com/natan-sysview/fast_parser</projectUrl>
    <repository type="git" url="https://github.com/natan-sysview/fast_parser" />
    <tags>fastparse tree-sitter parser {escape(language)} native</tags>
    <readme>README.md</readme>
    <dependencies>
      <group targetFramework="net8.0">
        <dependency id="FastParser" version="{escape(core_version)}" exclude="Build,Analyzers" />
      </group>
      <group targetFramework="net9.0">
        <dependency id="FastParser" version="{escape(core_version)}" exclude="Build,Analyzers" />
      </group>
    </dependencies>
    <contentFiles>
      <files include="any/any/fastparse/languages/{escape(language)}/manifest.json" buildAction="Content" copyToOutput="true" />
      <files include="any/any/fastparse/languages/{escape(language)}/queries/**/*.scm" buildAction="Content" copyToOutput="true" />
    </contentFiles>
  </metadata>
</package>
''',
        encoding="utf-8",
    )
    return nuspec


def write_opc_metadata(staging: Path, package_name: str, version: str) -> tuple[Path, Path, Path]:
    metadata_id = uuid.uuid4().hex
    created = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    rels = staging / "_rels" / ".rels"
    rels.parent.mkdir(parents=True, exist_ok=True)
    rels.write_text(
        f'''<?xml version="1.0" encoding="utf-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Type="http://schemas.microsoft.com/packaging/2010/07/manifest" Target="/{escape(package_name)}.nuspec" Id="R{metadata_id[:16]}" />
  <Relationship Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="/package/services/metadata/core-properties/{metadata_id}.psmdcp" Id="R{metadata_id[16:]}" />
</Relationships>
''',
        encoding="utf-8",
    )

    content_types = staging / "[Content_Types].xml"
    content_types.write_text(
        '''<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />
  <Default Extension="psmdcp" ContentType="application/vnd.openxmlformats-package.core-properties+xml" />
  <Default Extension="dll" ContentType="application/octet" />
  <Default Extension="dylib" ContentType="application/octet" />
  <Default Extension="so" ContentType="application/octet" />
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="md" ContentType="text/markdown" />
  <Default Extension="scm" ContentType="text/plain" />
  <Default Extension="targets" ContentType="application/xml" />
  <Override PartName="/''' + escape(package_name) + '''.nuspec" ContentType="application/octet" />
</Types>
''',
        encoding="utf-8",
    )

    core_props = staging / "package" / "services" / "metadata" / "core-properties" / f"{metadata_id}.psmdcp"
    core_props.parent.mkdir(parents=True, exist_ok=True)
    core_props.write_text(
        f'''<?xml version="1.0" encoding="utf-8"?>
<coreProperties xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns="http://schemas.openxmlformats.org/package/2006/metadata/core-properties">
  <dc:creator>natan-sysview</dc:creator>
  <dc:description>FastParse {escape(package_name)} language extension native assets.</dc:description>
  <dc:identifier>{escape(package_name)}</dc:identifier>
  <version>{escape(version)}</version>
  <keywords>fastparse tree-sitter parser native</keywords>
  <lastModifiedBy>NuGet, Version=6.0.0.0</lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">{created}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">{created}</dcterms:modified>
</coreProperties>
''',
        encoding="utf-8",
    )
    return rels, content_types, core_props


def make_package(staging: Path, nuspec: Path, output_dir: Path, package_name: str, version: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    package = output_dir / f"{package_name}.{version}.nupkg"
    if package.exists():
        package.unlink()
    write_opc_metadata(staging, package_name, version)
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for special in ["_rels/.rels", f"{package_name}.nuspec", "[Content_Types].xml"]:
            path = staging / special
            if path.is_file():
                zf.write(path, special)
        for path in sorted(staging.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(staging).as_posix()
            if relative in {"_rels/.rels", f"{package_name}.nuspec", "[Content_Types].xml"}:
                continue
            zf.write(path, relative)
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
        if args.require_all_rids and missing:
            raise AssertionError(f"missing required RID assets: {', '.join(missing)}")
        write_targets(args.language, staging)
        nuspec = write_nuspec(args.language, args.version, args.core_version or args.version, staging)
        package = make_package(staging, nuspec, args.output_dir.resolve(), package_id(args.language), args.version)
    print(f"NuGet language package: {package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
