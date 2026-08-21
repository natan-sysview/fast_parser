#!/usr/bin/env python3
"""Validate a local FastParser language extension NuGet package."""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


SOURCE = "https://api.nuget.org/v3/index.json"

PYTHON_PROGRAM = r'''using FastParse;

using var parser = new FastParseClient();

var load = parser.LoadBundledLanguage("python");
if (load.Language != "python" || !parser.LanguageAvailable("python"))
{
    throw new InvalidOperationException("FastParser.Language.Python load smoke failed");
}

var json = parser.ParseText(
    "def hello(name):\n    return name\n",
    new ParseOptions
    {
        Language = "python",
        Format = FastParseFormat.Json,
        IncludeRules = "function_definition",
        Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
    });

if (json.NodeCount != 1 || !json.Text.Contains("function_definition", StringComparison.Ordinal))
{
    throw new InvalidOperationException("FastParser.Language.Python JSON smoke failed");
}

var diagnostics = parser.ParseText(
    "def broken(\n",
    new ParseOptions
    {
        Language = "python",
        Format = FastParseFormat.Diagnostics
    });

using var diagnosticsDocument = diagnostics.JsonDocument();
if (diagnosticsDocument.RootElement.TryGetProperty("nodes", out _) ||
    !diagnosticsDocument.RootElement.GetProperty("hasErrors").GetBoolean())
{
    throw new InvalidOperationException("FastParser.Language.Python diagnostics smoke failed");
}

Console.WriteLine("FastParser language NuGet smoke OK");
Console.WriteLine(parser.Version);
Console.WriteLine(parser.LibraryPath);
'''

JAVA_FRAMEWORKS_PROGRAM = r'''using FastParse;

using var parser = new FastParseClient();

var load = parser.LoadBundledLanguage("java-frameworks");
if (load.Language != "java-frameworks" || !parser.LanguageAvailable("java-frameworks"))
{
    throw new InvalidOperationException("FastParser.Language.JavaFrameworks load smoke failed");
}

var source = "import org.springframework.stereotype.Service;\n@Service class Demo { void x(){ org.springframework.jdbc.core.JdbcTemplate t; } }\n";
var json = parser.ParseText(
    source,
    new ParseOptions
    {
        Language = "java-frameworks",
        Format = FastParseFormat.Json,
        Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
    });

if (json.NodeCount == 0 || !json.Text.Contains("program", StringComparison.Ordinal))
{
    throw new InvalidOperationException("FastParser.Language.JavaFrameworks JSON smoke failed");
}

var queryPath = Path.Combine(AppContext.BaseDirectory, "fastparse", "languages", "java-frameworks", "queries", "frameworks.scm");
if (!File.Exists(queryPath))
{
    throw new InvalidOperationException($"Framework query was not copied to output: {queryPath}");
}

var query = File.ReadAllText(queryPath);
var captures = parser.QueryText(
    source,
    query,
    new QueryOptions
    {
        Language = "java-frameworks",
        Format = FastParseFormat.Stats,
        Fields = FastParseField.CaptureName
    });

if (captures.NodeCount == 0)
{
    throw new InvalidOperationException("FastParser.Language.JavaFrameworks query smoke failed");
}

var diagnostics = parser.ParseText(
    "class Broken {",
    new ParseOptions
    {
        Language = "java-frameworks",
        Format = FastParseFormat.Diagnostics
    });

using var diagnosticsDocument = diagnostics.JsonDocument();
if (!diagnosticsDocument.RootElement.GetProperty("hasErrors").GetBoolean())
{
    throw new InvalidOperationException("FastParser.Language.JavaFrameworks diagnostics smoke failed");
}

Console.WriteLine("FastParser language NuGet smoke OK");
Console.WriteLine(parser.Version);
Console.WriteLine(parser.LibraryPath);
'''

JAVASWING_PROGRAM = r'''using FastParse;

using var parser = new FastParseClient();

var load = parser.LoadBundledLanguage("javaswing");
if (load.Language != "javaswing" || !parser.LanguageAvailable("javaswing"))
{
    throw new InvalidOperationException("FastParser.Language.JavaSwing load smoke failed");
}

var source = """
import javax.swing.*;
class Demo extends JFrame {
    JButton button = new JButton("OK");
    void build() {
        JPanel panel = new JPanel();
        panel.add(button);
    }
}
""";

var json = parser.ParseText(
    source,
    new ParseOptions
    {
        Language = "javaswing",
        Format = FastParseFormat.Json,
        IncludeRules = "javaswing_screen|javaswing_component_creation|javaswing_component_field|javaswing_container_add",
        Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
    });

if (json.NodeCount == 0 || !json.Text.Contains("javaswing_", StringComparison.Ordinal))
{
    throw new InvalidOperationException("FastParser.Language.JavaSwing JSON smoke failed");
}

var queryPath = Path.Combine(AppContext.BaseDirectory, "fastparse", "languages", "javaswing", "queries", "swing.scm");
if (!File.Exists(queryPath))
{
    throw new InvalidOperationException($"Swing query was not copied to output: {queryPath}");
}

var query = File.ReadAllText(queryPath);
var captures = parser.QueryTextSummary(
    source,
    query,
    new QueryOptions
    {
        Language = "javaswing",
        Format = FastParseFormat.Stats,
        Fields = FastParseField.CaptureName
    });

if (captures.NodeCount == 0)
{
    throw new InvalidOperationException("FastParser.Language.JavaSwing query smoke failed");
}

var diagnostics = parser.ParseText(
    "class Broken {",
    new ParseOptions
    {
        Language = "javaswing",
        Format = FastParseFormat.Diagnostics
    });

using var diagnosticsDocument = diagnostics.JsonDocument();
if (!diagnosticsDocument.RootElement.GetProperty("hasErrors").GetBoolean())
{
    throw new InvalidOperationException("FastParser.Language.JavaSwing diagnostics smoke failed");
}

Console.WriteLine("FastParser language NuGet smoke OK");
Console.WriteLine(parser.Version);
Console.WriteLine(parser.LibraryPath);
'''


COBOL_PROGRAM = r'''using System.Text;
using FastParse;

using var parser = new FastParseClient();

var load = parser.LoadBundledLanguage("cobol");
if (load.Language != "cobol" || !parser.LanguageAvailable("cobol"))
{
    throw new InvalidOperationException("FastParser.Language.Cobol load smoke failed");
}

var source = """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-NAME PIC X(10) VALUE 'CARLOS'.
       PROCEDURE DIVISION.
           DISPLAY WS-NAME.
           EXEC SQL
              COMMIT
           END-EXEC.
           GOBACK.
       END PROGRAM HELLO.
""";

var json = parser.ParseText(
    source,
    new ParseOptions
    {
        Language = "cobol",
        Format = FastParseFormat.Json,
        IncludeRules = "program_definition|exec_sql_statement|display_statement",
        Fields = FastParseField.Rule | FastParseField.Text | FastParseField.ByteRange
    });

if (json.NodeCount == 0 ||
    !json.Text.Contains("program_definition", StringComparison.Ordinal) ||
    !json.Text.Contains("exec_sql_statement", StringComparison.Ordinal))
{
    throw new InvalidOperationException("FastParser.Language.Cobol JSON smoke failed");
}

var diagnostics = parser.ParseText(
    source,
    new ParseOptions
    {
        Language = "cobol",
        Format = FastParseFormat.Diagnostics
    });

using var diagnosticsDocument = diagnostics.JsonDocument();
if (diagnosticsDocument.RootElement.GetProperty("hasErrors").GetBoolean())
{
    throw new InvalidOperationException("FastParser.Language.Cobol diagnostics smoke found errors");
}

var ebcdicCopybook = Convert.FromHexString("40404040404040F0F140D9C5C760E3C5D3C1F0F14B0D254040404040404040404040F0F240E2C4E3D4D6E5D4E3D640D7C9C340E74DF1F05D4B0D25");
var ebcdicDiagnostics = parser.ParseBytes(
    ebcdicCopybook,
    new ParseOptions
    {
        Language = "cobol",
        Format = FastParseFormat.Diagnostics,
        Normalization = FastParseNormalization.AutoSafe
    });

using var ebcdicDocument = ebcdicDiagnostics.JsonDocument();
if (ebcdicDocument.RootElement.GetProperty("hasErrors").GetBoolean())
{
    throw new InvalidOperationException("FastParser.Language.Cobol EBCDIC diagnostics smoke found errors");
}

var tabbedCopybook = Encoding.UTF8.GetBytes("       01 RCX11.\n\t 02 FCX11-CDEMP               PIC 9(02).\n");
var tabbedDiagnostics = parser.ParseBytes(
    tabbedCopybook,
    new ParseOptions
    {
        Language = "cobol",
        Format = FastParseFormat.Diagnostics,
        Normalization = FastParseNormalization.AutoSafe
    });

using var tabbedDocument = tabbedDiagnostics.JsonDocument();
if (tabbedDocument.RootElement.GetProperty("hasErrors").GetBoolean())
{
    throw new InvalidOperationException("FastParser.Language.Cobol tab-expanded diagnostics smoke found errors");
}

void AssertAutoSafeCobolClean(string name, string text)
{
    var result = parser.ParseBytes(
        Encoding.UTF8.GetBytes(text),
        new ParseOptions
        {
            Language = "cobol",
            Format = FastParseFormat.Diagnostics,
            Normalization = FastParseNormalization.AutoSafe
        });

    using var document = result.JsonDocument();
    if (document.RootElement.GetProperty("hasErrors").GetBoolean())
    {
        throw new InvalidOperationException($"FastParser.Language.Cobol fixed-layout normalization smoke failed: {name}");
    }
}

AssertAutoSafeCobolClean("left-shifted program", """
 IDENTIFICATION DIVISION.
 PROGRAM-ID. KNORRBK.
 DATA DIVISION.
 WORKING-STORAGE SECTION.
 01 WS-A PIC X.
 PROCEDURE DIVISION.
     GOBACK.
""");

AssertAutoSafeCobolClean("perform thru before paragraph", """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. PCL.
       PROCEDURE DIVISION.
       INICIO-PROGRAMA.
           PERFORM 000-TELA        THRU 000-SAI
      *
       010-INICIALIZACAO.
           GOBACK.
       000-TELA.
           EXIT.
       000-SAI.
           EXIT.
""");

AssertAutoSafeCobolClean("continuation to target", """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. VCP.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 MSGTXT PIC X(80).
       PROCEDURE DIVISION.
           IF MSGTXT = SPACES THEN
              MOVE 'IDENTIFICADOR (,991) NAO FOI INFORMADO'
      -                             TO MSGTXT
           ELSE
              GOBACK.
""");

Console.WriteLine("FastParser language NuGet smoke OK");
Console.WriteLine(parser.Version);
Console.WriteLine(parser.LibraryPath);
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a FastParser.Language.* package from local nupkgs.")
    parser.add_argument("--core-package", type=Path, required=True)
    parser.add_argument("--language-package", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--core-version", help="FastParser dependency version. Defaults to --version.")
    parser.add_argument("--language", default="python")
    parser.add_argument("--require-all-rids", action="store_true")
    return parser.parse_args()


def run_command(command: list[str], *, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stdout}")
    return completed


def package_language_name(language: str) -> str:
    if native_language_name(language) == "javaswing":
        return "JavaSwing"
    return "".join(part.capitalize() for part in language.replace("-", "_").split("_"))


def native_language_name(language: str) -> str:
    return language.strip().lower().replace("-", "_")


def native_file(language: str, rid: str) -> str:
    native = native_language_name(language)
    if rid.startswith("win-"):
        return f"fastparse_language_{native}.dll"
    if rid.startswith("osx-"):
        return f"libfastparse_language_{native}.dylib"
    return f"libfastparse_language_{native}.so"


def current_rid() -> str:
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


def smoke_framework(env: dict[str, str]) -> str:
    completed = run_command(["dotnet", "--list-sdks"], env=env)
    majors = []
    for line in completed.stdout.splitlines():
        version = line.split()[0] if line.split() else ""
        major = version.split(".", 1)[0]
        if major.isdigit():
            majors.append(int(major))
    if 9 in majors:
        return "net9.0"
    if 10 in majors:
        return "net10.0"
    if 8 in majors:
        return "net8.0"
    return "net9.0"


def validate_package_layout(language_package: Path, language: str, require_all_rids: bool) -> None:
    package_name = package_language_name(language)
    required = {
        "README.md",
        f"contentFiles/any/any/fastparse/languages/{language}/manifest.json",
        f"buildTransitive/FastParser.Language.{package_name}.targets",
    }
    rids = ("linux-x64", "osx-arm64", "osx-x64", "win-x64") if require_all_rids else (current_rid(),)
    for rid in rids:
        required.add(f"runtimes/{rid}/native/{native_file(language, rid)}")
    if language == "java-frameworks":
        required.add(f"contentFiles/any/any/fastparse/languages/{language}/queries/frameworks.scm")
    if language == "javaswing":
        required.add(f"contentFiles/any/any/fastparse/languages/{language}/queries/swing.scm")
    with zipfile.ZipFile(language_package) as zf:
        names = set(zf.namelist())
    missing = sorted(required - names)
    if missing:
        raise AssertionError(f"language NuGet package missing entries: {', '.join(missing)}")


def main() -> int:
    args = parse_args()
    core_version = args.core_version or args.version
    core_package = args.core_package.resolve()
    language_package = args.language_package.resolve()
    if not core_package.is_file():
        raise FileNotFoundError(core_package)
    if not language_package.is_file():
        raise FileNotFoundError(language_package)
    validate_package_layout(language_package, args.language, args.require_all_rids)

    print("Local language NuGet smoke environment", flush=True)
    print(f"  Python  : {platform.python_version()} {platform.platform()}", flush=True)
    print(f"  Machine : {platform.machine()}", flush=True)
    dotnet_info = run_command(["dotnet", "--info"], env=os.environ.copy())
    print(dotnet_info.stdout, flush=True)

    with tempfile.TemporaryDirectory(prefix="fastparser-language-nuget-smoke-") as temp:
        temp_dir = Path(temp)
        package_source = temp_dir / "packages"
        package_source.mkdir()
        shutil.copy2(core_package, package_source / core_package.name)
        shutil.copy2(language_package, package_source / language_package.name)

        project_dir = temp_dir / "consumer"
        env = os.environ.copy()
        env["NUGET_PACKAGES"] = str(temp_dir / "global-packages")
        env.pop("FASTPARSE_LIBRARY_PATH", None)
        env.pop("TSMP_LIBRARY_PATH", None)
        env.pop(f"FASTPARSE_LANGUAGE_{native_language_name(args.language).upper()}_PATH", None)

        run_command(
            ["dotnet", "new", "console", "--framework", smoke_framework(env), "--output", str(project_dir)],
            env=env,
        )
        project = str(project_dir / "consumer.csproj")
        run_command(
            ["dotnet", "add", project, "package", "FastParser", "--version", core_version, "--source", str(package_source)],
            env=env,
        )
        run_command(
            [
                "dotnet",
                "add",
                project,
                "package",
                f"FastParser.Language.{package_language_name(args.language)}",
                "--version",
                args.version,
                "--source",
                str(package_source),
            ],
            env=env,
        )
        if args.language == "java-frameworks":
            program = JAVA_FRAMEWORKS_PROGRAM
        elif args.language == "javaswing":
            program = JAVASWING_PROGRAM
        elif args.language == "cobol":
            program = COBOL_PROGRAM
        else:
            program = PYTHON_PROGRAM
        (project_dir / "Program.cs").write_text(program, encoding="utf-8")
        completed = run_command(["dotnet", "run", "--project", project], env=env)
        if "FastParser language NuGet smoke OK" not in completed.stdout:
            raise AssertionError(f"language NuGet smoke failed:\n{completed.stdout}")

    print(f"Validated local language NuGet package: {language_package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
