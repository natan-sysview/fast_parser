#!/usr/bin/env python3
"""Create a portable Windows x64 FastParse Java + JavaSwing distribution kit."""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "java" / "02_javaswing_extension" / "JavaSwingExtensionExample.java"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a self-contained Windows x64 FastParse Java + JavaSwing ZIP."
    )
    parser.add_argument("--version", required=True)
    parser.add_argument("--jar", type=Path, required=True, help="FastParse Java binding JAR")
    parser.add_argument(
        "--extension-archive",
        type=Path,
        required=True,
        help="Windows x64 JavaSwing language extension archive",
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "java-kits")
    return parser.parse_args()


def safe_extract(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            target = (destination / member.filename).resolve()
            if destination.resolve() not in target.parents and target != destination.resolve():
                raise ValueError(f"Archive member escapes destination: {member.filename}")
        zf.extractall(destination)


def require_member(archive: Path, member: str) -> None:
    with zipfile.ZipFile(archive) as zf:
        if member not in zf.namelist():
            raise ValueError(f"{archive.name} is missing required member: {member}")


def find_extension_root(extracted: Path, version: str) -> Path:
    expected = extracted / f"fastparse-language-javaswing-{version}-windows-x64"
    if not expected.is_dir():
        raise FileNotFoundError(f"Expected JavaSwing extension directory: {expected}")
    required = [
        expected / "manifest.json",
        expected / "README.md",
        expected / "native" / "win-x64" / "fastparse_language_javaswing.dll",
        expected / "queries" / "swing.scm",
    ]
    missing = [str(path.relative_to(expected)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"JavaSwing extension archive is incomplete: {', '.join(missing)}")
    return expected


def start_here(version: str) -> str:
    return f"""# FastParse Java + JavaSwing for Windows x64

This portable kit contains FastParse {version}, the Java 8+ JNI binding, and the
JavaSwing Tree-sitter grammar. It does not require Maven, NuGet, Python, or a C/C++
toolchain on the target computer.

## Requirements

- Windows x64
- A JDK 8 or newer. A JRE alone cannot compile the included example.

## First run

1. Extract this ZIP somewhere writable, for example `C:\\tools\\fastparse`.
2. Open Command Prompt in the extracted directory.
3. Run `run-example.bat`.

The script compiles and runs `examples\\JavaSwingExtensionExample.java`. The Java
binding automatically extracts `fastparse.dll` and `fastparse_jni.dll` from the JAR
to the JVM temporary directory. The example explicitly loads:

`extensions\\javaswing\\native\\win-x64\\fastparse_language_javaswing.dll`

## Add it to another Java project

Copy `lib\\fastparse-{version}.jar` into that project's local `lib` directory and
reference it on the Java classpath. Copy the `extensions\\javaswing` directory with
the project, then load its DLL before parsing:

```java
try (FastParseClient client = FastParseClient.open()) {{
    client.loadLanguageExtension("path\\\\to\\\\fastparse_language_javaswing.dll");
    ParseResult result = client.parseText(source,
        ParseOptions.builder().language("javaswing").build());
}}
```

Load extensions before starting concurrent parser workers. Parsing source text and
returning the AST occur in memory; FastParse does not create temporary source files.

## Documentation

- `docs\\FASTPARSE.md`: full project documentation.
- `docs\\AI_AGENT_GUIDE.md`: contracts and guidance for AI agents.
- `docs\\JAVA_BINDING.md`: Java API, native loading, threading, and output formats.
- `docs\\JAVASWING_EXTENSION.md`: JavaSwing grammar and queries.
"""


def run_example(version: str) -> str:
    return f"""@echo off
setlocal
set "KIT_ROOT=%~dp0"
set "JAR=%KIT_ROOT%lib\\fastparse-{version}.jar"
set "OUT=%KIT_ROOT%out"

where javac >nul 2>nul
if errorlevel 1 (
  echo ERROR: A JDK 8 or newer is required. javac was not found on PATH.
  exit /b 1
)

if not exist "%JAR%" (
  echo ERROR: FastParse JAR was not found: %JAR%
  exit /b 1
)

if not exist "%KIT_ROOT%extensions\\javaswing\\native\\win-x64\\fastparse_language_javaswing.dll" (
  echo ERROR: JavaSwing extension DLL is missing from this kit.
  exit /b 1
)

if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%"

javac -encoding UTF-8 -cp "%JAR%" -d "%OUT%" "%KIT_ROOT%examples\\JavaSwingExtensionExample.java"
if errorlevel 1 exit /b %errorlevel%

java -cp "%JAR%;%OUT%" JavaSwingExtensionExample
exit /b %errorlevel%
"""


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def package(args: argparse.Namespace) -> Path:
    jar = args.jar.resolve()
    extension_archive = args.extension_archive.resolve()
    if not jar.is_file():
        raise FileNotFoundError(jar)
    if not extension_archive.is_file():
        raise FileNotFoundError(extension_archive)
    if not EXAMPLE.is_file():
        raise FileNotFoundError(EXAMPLE)

    require_member(jar, "dev/fastparse/FastParseClient.class")
    require_member(jar, "dev/fastparse/native/windows-x64/fastparse.dll")
    require_member(jar, "dev/fastparse/native/windows-x64/fastparse_jni.dll")

    kit_name = f"fastparse-java-javaswing-{args.version}-windows-x64"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / f"{kit_name}.zip"
    if output.exists():
        output.unlink()

    with tempfile.TemporaryDirectory(prefix="fastparse-javaswing-kit-") as tmp:
        temp = Path(tmp)
        safe_extract(extension_archive, temp)
        extension_root = find_extension_root(temp, args.version)

        kit_root = temp / kit_name
        copy_file(jar, kit_root / "lib" / f"fastparse-{args.version}.jar")
        shutil.copytree(extension_root, kit_root / "extensions" / "javaswing")
        copy_file(EXAMPLE, kit_root / "examples" / EXAMPLE.name)

        docs = {
            ROOT / "README.md": "FASTPARSE.md",
            ROOT / "AI_AGENT_GUIDE.md": "AI_AGENT_GUIDE.md",
            ROOT / "bindings" / "java" / "fastparse" / "README.md": "JAVA_BINDING.md",
            ROOT / "extensions" / "javaswing" / "README.md": "JAVASWING_EXTENSION.md",
            ROOT / "LICENSE": "LICENSE.txt",
            ROOT / "NOTICE": "NOTICE.txt",
        }
        for source, name in docs.items():
            copy_file(source, kit_root / "docs" / name)

        (kit_root / "START-HERE.md").write_text(start_here(args.version), encoding="utf-8")
        (kit_root / "run-example.bat").write_text(run_example(args.version), encoding="utf-8", newline="\r\n")
        (kit_root / "kit-manifest.json").write_text(json.dumps({
            "name": "FastParse Java + JavaSwing Windows kit",
            "version": args.version,
            "platform": "windows-x64",
            "java": "8+",
            "coreJar": f"lib/fastparse-{args.version}.jar",
            "extension": "javaswing",
            "extensionLibrary": "extensions/javaswing/native/win-x64/fastparse_language_javaswing.dll",
        }, indent=2) + "\n", encoding="utf-8")

        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(kit_root.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(temp))
    return output


def main() -> int:
    args = parse_args()
    output = package(args)
    print(f"Windows Java + JavaSwing kit: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
