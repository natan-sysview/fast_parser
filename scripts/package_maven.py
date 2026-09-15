#!/usr/bin/env python3
"""Package/publish the FastParse Java/JNI Maven artifact with platform native resources.

The script copies the Maven project into a temporary workspace before injecting native
resources and setting the release version. This keeps the repository clean during local
packaging and CI validation.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA_PROJECT = ROOT / "bindings/java/fastparse"
DIST = ROOT / "dist/maven"
RESOURCE_REL = Path("src/main/resources/dev/fastparse/native")
REQUIRED_RIDS = {"linux-x64", "macos-x64", "macos-arm64", "windows-x64"}

CORE_RE = re.compile(r"fastparse-(?P<version>.+)-(?P<platform>linux|macos|windows)-(?P<arch>x64|arm64)\.(?:tar\.gz|zip)$")
JNI_RE = re.compile(r"fastparse-java-jni-(?P<version>.+)-(?P<platform>linux|macos|windows)-(?P<arch>x64|arm64)\.(?:tar\.gz|zip)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or publish the FastParse Maven artifact.")
    parser.add_argument("--version", required=True)
    parser.add_argument("--archive", action="append", default=[], help="FastParse core release archive")
    parser.add_argument("--jni-archive", action="append", default=[], help="FastParse Java JNI bridge archive")
    parser.add_argument("--output-dir", type=Path, default=DIST)
    parser.add_argument("--require-all-rids", action="store_true")
    parser.add_argument("--deploy", action="store_true", help="Run mvn deploy using the release profile")
    parser.add_argument("--skip-maven", action="store_true")
    return parser.parse_args()


def rid(platform_name: str, arch: str) -> str:
    return f"{platform_name}-{arch}"


def core_file(platform_name: str) -> str:
    if platform_name == "windows":
        return "fastparse.dll"
    if platform_name == "macos":
        return "libfastparse.dylib"
    return "libfastparse.so"


def jni_file(platform_name: str) -> str:
    if platform_name == "windows":
        return "fastparse_jni.dll"
    if platform_name == "macos":
        return "libfastparse_jni.dylib"
    return "libfastparse_jni.so"


def extract_archive(archive: Path, dest: Path) -> None:
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(dest)
    else:
        with tarfile.open(archive, "r:gz") as tf:
            tf.extractall(dest)


def find_file(directory: Path, name: str) -> Path:
    matches = [candidate for candidate in directory.rglob(name) if candidate.is_file()]
    if not matches:
        raise FileNotFoundError(f"{name} not found in extracted archive {directory}")
    return matches[0]


def copy_native_from_archives(
    project_dir: Path,
    archives: list[str],
    pattern: re.Pattern[str],
    file_name_fn,
    expected_version: str,
) -> set[str]:
    copied: set[str] = set()
    for raw in archives:
        archive = Path(raw).resolve()
        match = pattern.match(archive.name)
        if not match:
            raise ValueError(f"Unexpected archive name: {archive.name}")
        if match.group("version") != expected_version:
            raise ValueError(f"Archive {archive.name} does not match version {expected_version}")
        platform_name = match.group("platform")
        arch = match.group("arch")
        target_rid = rid(platform_name, arch)
        with tempfile.TemporaryDirectory(prefix="fastparse-maven-archive-") as td:
            tmp = Path(td)
            extract_archive(archive, tmp)
            wanted = file_name_fn(platform_name)
            src = find_file(tmp, wanted)
            out_dir = project_dir / RESOURCE_REL / target_rid
            out_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, out_dir / wanted)
            copied.add(target_rid)
    return copied


def copy_java_project(temp_root: Path) -> Path:
    if not JAVA_PROJECT.is_dir():
        raise FileNotFoundError(JAVA_PROJECT)

    def ignore(dir_name: str, names: list[str]) -> set[str]:
        ignored = {"target"} & set(names)
        path = Path(dir_name)
        if path.match("*/src/main/resources/dev/fastparse") and "native" in names:
            ignored.add("native")
        return ignored

    project_dir = temp_root / "fastparse-maven-project"
    shutil.copytree(JAVA_PROJECT, project_dir, ignore=ignore)
    return project_dir


def set_pom_version(project_dir: Path, version: str) -> None:
    pom = project_dir / "pom.xml"
    ET.register_namespace("", "http://maven.apache.org/POM/4.0.0")
    tree = ET.parse(pom)
    root = tree.getroot()
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    version_el = root.find("m:version", ns)
    if version_el is None:
        raise RuntimeError("pom.xml has no project version")
    version_el.text = version
    tree.write(pom, encoding="UTF-8", xml_declaration=True)


def run_maven(project_dir: Path, output_dir: Path, deploy: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    goal = "deploy" if deploy else "verify"
    cmd = ["mvn", "-q", "-f", str(project_dir / "pom.xml"), "-DskipTests"]
    if deploy:
        cmd.extend(["-P", "release"])
    cmd.append(goal)
    env = os.environ.copy()
    if "GPG_PASSPHRASE" in env and "MAVEN_GPG_PASSPHRASE" not in env:
        env["MAVEN_GPG_PASSPHRASE"] = env["GPG_PASSPHRASE"]
    subprocess.run(cmd, cwd=str(project_dir), env=env, check=True)
    for artifact in (project_dir / "target").glob("fastparse-*"):
        if artifact.is_file() and artifact.suffix in {".jar", ".pom", ".asc", ".zip"}:
            shutil.copy2(artifact, output_dir / artifact.name)
    pom = project_dir / "pom.xml"
    shutil.copy2(pom, output_dir / f"fastparse-{project_version(project_dir)}.pom")


def project_version(project_dir: Path) -> str:
    tree = ET.parse(project_dir / "pom.xml")
    root = tree.getroot()
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    return root.findtext("m:version", namespaces=ns) or "unknown"


def main() -> int:
    args = parse_args()
    with tempfile.TemporaryDirectory(prefix="fastparse-maven-project-") as td:
        project_dir = copy_java_project(Path(td))
        set_pom_version(project_dir, args.version)
        core_rids = copy_native_from_archives(project_dir, args.archive, CORE_RE, core_file, args.version)
        jni_rids = copy_native_from_archives(project_dir, args.jni_archive, JNI_RE, jni_file, args.version)
        complete_rids = core_rids & jni_rids
        missing = REQUIRED_RIDS - complete_rids
        if args.require_all_rids and missing:
            raise SystemExit(f"Missing complete native resources for RIDs: {sorted(missing)}")
        if not args.skip_maven:
            run_maven(project_dir, args.output_dir.resolve(), args.deploy)
        print(f"Maven resources ready. Core RIDs={sorted(core_rids)} JNI RIDs={sorted(jni_rids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
