#!/usr/bin/env python3
"""Smoke-test a local FastParse language extension."""

from __future__ import annotations

import argparse
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from fastparse import FastParse, OutputFormat, ParseOptions  # noqa: E402


JAVA_FRAMEWORKS_SOURCE = """
import javax.faces.bean.ManagedBean;
import javax.faces.bean.ViewScoped;
import javax.faces.context.FacesContext;
import javax.faces.application.FacesMessage;
import org.primefaces.PrimeFaces;
import org.springframework.stereotype.Service;
import org.springframework.jdbc.core.JdbcTemplate;

@ManagedBean(name = "demoBean")
@ViewScoped
@Service
class DemoBean {
  private JdbcTemplate jdbcTemplate;

  void show() {
    FacesContext.getCurrentInstance().addMessage(null, new FacesMessage("OK"));
    PrimeFaces.current().ajax().update("form:panel");
  }
}
""".strip()


PLSQL_SOURCE = """
CREATE OR REPLACE PACKAGE BODY demo_pkg AS
  PROCEDURE parent_proc IS
    FUNCTION child_func RETURN NUMBER IS
    BEGIN
      RETURN 1;
    END child_func;
  BEGIN
    INSERT INTO demo_table(id, name) VALUES (child_func(), 'OK');
  END parent_proc;
END demo_pkg;
/
""".strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a local FastParse language extension.")
    parser.add_argument("--language", required=True)
    parser.add_argument("--library", type=Path, default=default_core_library())
    parser.add_argument("--extension", type=Path)
    parser.add_argument("--query", type=Path)
    return parser.parse_args()


def default_core_library() -> Path:
    if sys.platform == "darwin":
        return ROOT / "bin" / "libfastparse.dylib"
    if sys.platform == "win32":
        return ROOT / "bin" / "fastparse.dll"
    return ROOT / "bin" / "libfastparse.so"


def default_extension_library(language: str) -> Path:
    native = language.strip().lower().replace("-", "_")
    if sys.platform == "darwin":
        return ROOT / "bin" / f"libfastparse_language_{native}.dylib"
    if sys.platform == "win32":
        return ROOT / "bin" / f"fastparse_language_{native}.dll"
    return ROOT / "bin" / f"libfastparse_language_{native}.so"


def default_query(language: str) -> Path:
    if language == "java-frameworks":
        return ROOT / "extensions" / language / "queries" / "frameworks.scm"
    return ROOT / "extensions" / language / "queries" / f"{language}.scm"


def validate_java_frameworks(parser: FastParse, query_path: Path) -> None:
    json_result = parser.parse_text(
        JAVA_FRAMEWORKS_SOURCE,
        ParseOptions(
            language="java-frameworks",
            output_format=OutputFormat.JSON,
            fields=["rule", "text", "byte_range"],
        ),
    )
    document = json_result.json()
    rules = {node["rule"] for node in document.get("nodes", []) if "rule" in node}
    required_rules = {"jsf_context_method_invocation", "primefaces_backend_method_invocation"}
    missing_rules = sorted(required_rules - rules)
    if missing_rules:
        raise AssertionError(f"missing expected java-frameworks rules: {missing_rules}")

    binary_result = parser.parse_text(
        JAVA_FRAMEWORKS_SOURCE,
        language="java-frameworks",
        output_format=OutputFormat.BINARY,
        fields=["rule", "text", "byte_range"],
    )
    binary_document = binary_result.binary_document()
    if binary_document.language != "java-frameworks" or binary_document.node_count <= 0:
        raise AssertionError(f"invalid MessagePack document: {binary_document}")

    query = query_path.read_text(encoding="utf-8")
    capture_summary = parser.query_text_summary(
        JAVA_FRAMEWORKS_SOURCE,
        query,
        language="java-frameworks",
        output_format=OutputFormat.STATS,
        fields=["capture_name"],
    )
    if capture_summary.node_count <= 0:
        raise AssertionError("frameworks query returned zero captures")

    diagnostics = parser.parse_text(
        "class Broken {",
        language="java-frameworks",
        output_format=OutputFormat.DIAGNOSTICS,
    ).json()
    if diagnostics.get("hasErrors") is not True:
        raise AssertionError(f"diagnostics did not report parse recovery: {diagnostics}")

    print(
        "FastParse java-frameworks extension smoke OK "
        f"({platform.system()} {platform.machine()}, captures={capture_summary.node_count})"
    )


def validate_plsql(parser: FastParse) -> None:
    json_result = parser.parse_text(
        PLSQL_SOURCE,
        ParseOptions(
            language="plsql",
            output_format=OutputFormat.JSON,
            fields=["rule", "text", "byte_range"],
        ),
    )
    document = json_result.json()
    rules = {node["rule"] for node in document.get("nodes", []) if "rule" in node}
    required_rules = {"create_package_body", "procedure_definition", "nested_function_definition"}
    missing_rules = sorted(required_rules - rules)
    if missing_rules:
        raise AssertionError(f"missing expected plsql rules: {missing_rules}")

    diagnostics = parser.parse_text(
        PLSQL_SOURCE,
        language="plsql",
        output_format=OutputFormat.DIAGNOSTICS,
    ).json()
    if diagnostics.get("hasErrors") is True:
        raise AssertionError(f"plsql smoke unexpectedly has parse errors: {diagnostics}")

    cursor_source = (
        "CREATE PACKAGE p IS "
        "CURSOR c IS WITH d AS (SELECT app.workday(1) d FROM dual ORDER BY d), "
        "m AS (SELECT app.next_workday(2) d FROM dual) SELECT d FROM d; "
        "CURSOR c2 IS SELECT x FROM t; END; /"
    )
    cursor_document = parser.parse_text(
        cursor_source,
        language="plsql",
        output_format=OutputFormat.BINARY,
        include_rules=["cursor_definition", "ref_call", "legacy_package_spec_cursor_definition_blob"],
        fields=["rule", "text", "range", "diagnostics"],
    ).binary_document()
    cursor_rules = [node.rule for node in cursor_document.nodes]
    call_texts = {node.text for node in cursor_document.nodes if node.rule == "ref_call"}
    if (
        cursor_document.has_errors
        or cursor_rules.count("cursor_definition") != 2
        or "legacy_package_spec_cursor_definition_blob" in cursor_rules
        or not {b"app.workday(1)", b"app.next_workday(2)"} <= call_texts
    ):
        raise AssertionError(f"plsql cursor structure was lost: {cursor_document}")

    type_source = (
        'CREATE TYPE "demo"."item_t" AS OBJECT (id NUMBER) NOT FINAL NOT INSTANTIABLE; '
        'CREATE TYPE item_list_t AS TABLE OF item_t; '
        'CREATE TYPE BODY item_t IS '
        'CONSTRUCTOR FUNCTION item_t RETURN SELF AS RESULT IS '
        'BEGIN RETURN; END; END;'
    )
    type_document = parser.parse_text(
        type_source,
        language="plsql",
        output_format=OutputFormat.BINARY,
        include_rules=["create_type", "create_type_body", "type_constructor_definition"],
        fields=["rule", "range", "diagnostics"],
    ).binary_document()
    type_counts = {rule: sum(node.rule == rule for node in type_document.nodes) for rule in
                   ("create_type", "create_type_body", "type_constructor_definition")}
    if type_document.has_errors or type_counts != {
        "create_type": 2,
        "create_type_body": 1,
        "type_constructor_definition": 1,
    }:
        raise AssertionError(f"plsql Oracle type structure was lost: {type_counts}, {type_document}")

    broken = parser.parse_text(
        "CREATE TABLE broken_table (id NUMBER",
        language="plsql",
        output_format=OutputFormat.DIAGNOSTICS,
    ).json()
    if broken.get("hasErrors") is not True:
        raise AssertionError(f"plsql diagnostics did not report broken source: {broken}")

    print(
        "FastParse plsql extension smoke OK "
        f"({platform.system()} {platform.machine()}, nodes={json_result.node_count})"
    )


def validate_generic(parser: FastParse, language: str) -> None:
    result = parser.parse_text(
        "class Demo { void run() {} }",
        language=language,
        output_format=OutputFormat.JSON,
        fields=["rule", "text"],
    )
    if result.node_count <= 0:
        raise AssertionError(f"{language} parse returned zero nodes")
    print(f"FastParse {language} extension smoke OK")


def main() -> int:
    args = parse_args()
    language = args.language.strip().lower()
    extension = args.extension or default_extension_library(language)
    query = args.query or default_query(language)

    if not args.library.is_file():
        raise FileNotFoundError(f"FastParse native library not found: {args.library}")
    if not extension.is_file():
        raise FileNotFoundError(f"FastParse language extension not found: {extension}")

    parser = FastParse(args.library)
    load = parser.load_language_extension(extension)
    if load.language != language or not parser.language_available(language):
        raise AssertionError(f"extension loaded incorrectly: {load}")

    if language == "java-frameworks":
        if not query.is_file():
            raise FileNotFoundError(f"java-frameworks query not found: {query}")
        validate_java_frameworks(parser, query)
    elif language == "plsql":
        validate_plsql(parser)
    else:
        validate_generic(parser, language)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
