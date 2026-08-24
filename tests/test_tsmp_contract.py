#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from fastparse import FastParse  # noqa: E402
from tsmp import (  # noqa: E402
    Field,
    NativeParseError,
    Normalization,
    OutputFormat,
    ParseOptions,
    QueryOptions,
    Tsmp,
    decode_binary,
    default_library_path,
    parse_field_mask,
)


SOURCE_PATH = ROOT / "file_test" / "java" / "HelloWorld.java"


def test_language_extension_path() -> Path:
    if sys.platform == "darwin":
        name = "libfastparse_language_test_java.dylib"
    elif sys.platform == "win32":
        name = "fastparse_language_test_java.dll"
    else:
        name = "libfastparse_language_test_java.so"
    return ROOT / "bin" / name


def cobol_language_extension_path() -> Path:
    if sys.platform == "darwin":
        name = "libfastparse_language_cobol.dylib"
    elif sys.platform == "win32":
        name = "fastparse_language_cobol.dll"
    else:
        name = "libfastparse_language_cobol.so"
    return ROOT / "bin" / name


def python_language_extension_path() -> Path:
    if sys.platform == "darwin":
        name = "libfastparse_language_python.dylib"
    elif sys.platform == "win32":
        name = "fastparse_language_python.dll"
    else:
        name = "libfastparse_language_python.so"
    return ROOT / "bin" / name


def rust_language_extension_path() -> Path:
    if sys.platform == "darwin":
        name = "libfastparse_language_rust.dylib"
    elif sys.platform == "win32":
        name = "fastparse_language_rust.dll"
    else:
        name = "libfastparse_language_rust.so"
    return ROOT / "bin" / name


def load_cobol_extension(parser: Tsmp, extension_path: Path) -> None:
    if not parser.language_available("cobol"):
        parser.load_language_extension(extension_path)


class MiniMsgpack:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.index = 0

    def read(self) -> Any:
        code = self._u8()
        if code <= 0x7F:
            return code
        if 0x80 <= code <= 0x8F:
            return self._map(code & 0x0F)
        if 0x90 <= code <= 0x9F:
            return self._array(code & 0x0F)
        if 0xA0 <= code <= 0xBF:
            return self._bytes(code & 0x1F).decode("utf-8")
        if code == 0xC0:
            return None
        if code == 0xC2:
            return False
        if code == 0xC3:
            return True
        if code == 0xC4:
            return self._bytes(self._u8())
        if code == 0xC5:
            return self._bytes(self._u16())
        if code == 0xC6:
            return self._bytes(self._u32())
        if code == 0xCC:
            return self._u8()
        if code == 0xCD:
            return self._u16()
        if code == 0xCE:
            return self._u32()
        if code == 0xCF:
            return self._u64()
        if code == 0xD9:
            return self._bytes(self._u8()).decode("utf-8")
        if code == 0xDA:
            return self._bytes(self._u16()).decode("utf-8")
        if code == 0xDB:
            return self._bytes(self._u32()).decode("utf-8")
        if code == 0xDC:
            return self._array(self._u16())
        if code == 0xDD:
            return self._array(self._u32())
        if code == 0xDE:
            return self._map(self._u16())
        if code == 0xDF:
            return self._map(self._u32())
        raise AssertionError(f"unsupported msgpack code: 0x{code:02x}")

    def _array(self, count: int) -> list[Any]:
        return [self.read() for _ in range(count)]

    def _map(self, count: int) -> dict[Any, Any]:
        return {self.read(): self.read() for _ in range(count)}

    def _bytes(self, length: int) -> bytes:
        end = self.index + length
        value = self.data[self.index:end]
        self.index = end
        return value

    def _u8(self) -> int:
        value = self.data[self.index]
        self.index += 1
        return value

    def _u16(self) -> int:
        value = int.from_bytes(self.data[self.index : self.index + 2], "big")
        self.index += 2
        return value

    def _u32(self) -> int:
        value = int.from_bytes(self.data[self.index : self.index + 4], "big")
        self.index += 4
        return value

    def _u64(self) -> int:
        value = int.from_bytes(self.data[self.index : self.index + 8], "big")
        self.index += 8
        return value


def unpack_msgpack(data: bytes) -> Any:
    decoder = MiniMsgpack(data)
    value = decoder.read()
    if decoder.index != len(data):
        raise AssertionError("trailing MessagePack bytes")
    return value


class TsmpContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SOURCE_PATH.read_bytes()
        cls.tsmp = Tsmp(default_library_path())

    def parse_result(self, **kwargs):
        return self.tsmp.parse_result(self.source, language="java", **kwargs)

    def test_json_default_exploration_returns_all_fields(self) -> None:
        output, node_count = self.parse_result(output_format="json")
        document = json.loads(output)

        self.assertEqual(document["language"], "java")
        self.assertEqual(document["nodeCount"], node_count)
        self.assertEqual(node_count, 100)

        first = document["nodes"][0]
        self.assertEqual(first["rule"], "program")
        self.assertIn("text", first)
        self.assertIn("children", first)
        self.assertIn("startLine", first)
        self.assertIn("startByte", first)

    def test_json_filters_rules_and_fields(self) -> None:
        fields = parse_field_mask("id,parent_id,rule,range,child_count")
        output, node_count = self.parse_result(
            output_format="json",
            include_rules="class_declaration|method_declaration",
            fields=fields,
        )
        document = json.loads(output)

        self.assertEqual(node_count, 2)
        self.assertEqual([node["rule"] for node in document["nodes"]], ["class_declaration", "method_declaration"])
        self.assertNotIn("text", document["nodes"][0])
        self.assertIn("startLine", document["nodes"][0])

    def test_python_binding_accepts_lists_for_rules_and_fields(self) -> None:
        result = self.tsmp.parse_bytes(
            self.source,
            output_format="json",
            include_rules=["class_declaration", "method_declaration"],
            fields=["rule", "byte_range"],
        )
        document = result.json()

        self.assertEqual(result.node_count, 2)
        self.assertEqual([node["rule"] for node in document["nodes"]], ["class_declaration", "method_declaration"])
        self.assertIn("startByte", document["nodes"][0])
        self.assertNotIn("text", document["nodes"][0])

    def test_python_binding_parse_text(self) -> None:
        result = self.tsmp.parse_text(
            "class Demo { void run() {} }",
            output_format="json",
            include_rules=["method_declaration"],
            fields=["rule", "text"],
        )
        document = result.json()

        self.assertEqual(result.output_format, "json")
        self.assertEqual(result.node_count, 1)
        self.assertEqual(document["nodes"][0]["rule"], "method_declaration")

    def test_python_binding_accepts_parse_options_and_enums(self) -> None:
        options = ParseOptions(
            output_format=OutputFormat.JSON,
            include_rules=["method_declaration"],
            fields=Field.RULE | Field.TEXT | Field.BYTE_RANGE,
            normalization=Normalization.AUTO_SAFE,
        )
        result = self.tsmp.parse_text("class Demo { void run() {} }", options)
        document = result.json()

        self.assertEqual(result.output_format, "json")
        self.assertEqual(result.node_count, 1)
        self.assertEqual(document["nodes"][0]["rule"], "method_declaration")
        self.assertIn("startByte", document["nodes"][0])

    def test_python_binding_options_can_be_overridden_per_call(self) -> None:
        options = ParseOptions(
            output_format=OutputFormat.STATS,
            include_rules=["method_declaration"],
            fields=Field.RULE,
        )
        result = self.tsmp.parse_text(
            "class Demo { void run() {} }",
            options,
            output_format=OutputFormat.JSON,
            fields=Field.RULE | Field.TEXT,
        )
        document = result.json()

        self.assertEqual(result.output_format, "json")
        self.assertEqual(document["nodes"][0]["rule"], "method_declaration")
        self.assertIn("text", document["nodes"][0])

    def test_python_binding_query_text_returns_captures(self) -> None:
        result = self.tsmp.query_text(
            "class Demo { void run() {} }",
            "(method_declaration name: (identifier) @method.name) @method",
        )
        document = result.json()

        self.assertEqual(result.output_format, "json")
        self.assertEqual(result.node_count, 2)
        self.assertEqual(document["language"], "java")
        self.assertEqual(document["matchCount"], 1)
        self.assertEqual(document["captureCount"], 2)
        method_name = next(capture for capture in document["matches"][0]["captures"] if capture["name"] == "method.name")
        self.assertEqual(method_name["rule"], "identifier")
        self.assertEqual(method_name["text"], "run")
        self.assertIn("startLine", method_name)
        self.assertIn("startByte", method_name)

    def test_python_binding_query_options_fields_and_limits(self) -> None:
        result = self.tsmp.query_text(
            "class Demo { void run() {} }",
            "(method_declaration name: (identifier) @method.name)",
            QueryOptions(
                fields=Field.CAPTURE_NAME | Field.TEXT,
                max_captures=1,
                include_pattern=False,
            ),
        )
        capture = result.json()["matches"][0]["captures"][0]

        self.assertEqual(result.node_count, 1)
        self.assertEqual(capture["name"], "method.name")
        self.assertEqual(capture["text"], "run")
        self.assertNotIn("rule", capture)
        self.assertNotIn("patternIndex", capture)

    def test_python_binding_query_binary_and_stats(self) -> None:
        query = "(method_declaration name: (identifier) @method.name) @method"
        binary = self.tsmp.query_text(
            "class Demo { void run() {} }",
            query,
            output_format=OutputFormat.BINARY,
        )
        document = unpack_msgpack(binary.data)

        self.assertEqual(document["format"], "fastparse-query-binary")
        self.assertEqual(document["language"], "java")
        self.assertEqual(document["matchCount"], 1)
        self.assertEqual(document["captureCount"], 2)
        method_name = next(capture for capture in document["matches"][0]["captures"] if capture["name"] == "method.name")
        self.assertEqual(method_name["text"], b"run")

        summary = self.tsmp.query_text_summary(
            "class Demo { void run() {} }",
            query,
            output_format=OutputFormat.STATS,
        )
        self.assertEqual(summary.output_format, "stats")
        self.assertEqual(summary.node_count, 2)
        self.assertEqual(summary.output_length, 1)

    def test_python_binding_invalid_query_raises(self) -> None:
        with self.assertRaises(NativeParseError):
            self.tsmp.query_text("class Demo {}", "(missing_node) @bad")

    def test_python_binding_parse_text_summary(self) -> None:
        summary = self.tsmp.parse_text_summary(
            "class Demo { void run() {} }",
            ParseOptions(
                output_format=OutputFormat.JSON,
                include_rules=["method_declaration"],
                fields=Field.RULE | Field.TEXT,
            ),
        )
        full = self.tsmp.parse_text(
            "class Demo { void run() {} }",
            output_format="json",
            include_rules=["method_declaration"],
            fields=["rule", "text"],
        )

        self.assertEqual(summary.node_count, full.node_count)
        self.assertEqual(summary.output_length, len(full.data))

    def test_python_binding_summary_does_not_copy_output(self) -> None:
        summary = self.tsmp.parse_bytes_summary(
            self.source,
            output_format="json",
            include_rules=["method_declaration"],
            fields=["rule", "text"],
        )
        full = self.tsmp.parse_bytes(
            self.source,
            output_format="json",
            include_rules=["method_declaration"],
            fields=["rule", "text"],
        )

        self.assertEqual(summary.node_count, full.node_count)
        self.assertEqual(summary.output_length, len(full.data))
        self.assertEqual(summary.output_format, "json")

    def test_default_library_path_honors_environment(self) -> None:
        old_value = os.environ.get("TSMP_LIBRARY_PATH")
        old_fastparse_value = os.environ.get("FASTPARSE_LIBRARY_PATH")
        custom_tsmp = ROOT / "custom" / "libtsmp.test"
        custom_fastparse = ROOT / "custom" / "libfastparse.test"
        try:
            os.environ.pop("FASTPARSE_LIBRARY_PATH", None)
            os.environ["TSMP_LIBRARY_PATH"] = str(custom_tsmp)
            self.assertEqual(default_library_path(), custom_tsmp)

            os.environ["FASTPARSE_LIBRARY_PATH"] = str(custom_fastparse)
            self.assertEqual(default_library_path(), custom_fastparse)
        finally:
            if old_value is None:
                os.environ.pop("TSMP_LIBRARY_PATH", None)
            else:
                os.environ["TSMP_LIBRARY_PATH"] = old_value
            if old_fastparse_value is None:
                os.environ.pop("FASTPARSE_LIBRARY_PATH", None)
            else:
                os.environ["FASTPARSE_LIBRARY_PATH"] = old_fastparse_value

    def test_fastparse_python_alias_works(self) -> None:
        parser = FastParse(default_library_path())
        result = parser.parse_bytes(
            self.source,
            output_format="json",
            include_rules=["method_declaration"],
            fields=["rule"],
        )

        self.assertEqual(result.json()["nodes"][0]["rule"], "method_declaration")

    def test_csv_respects_rules_and_fields(self) -> None:
        fields = parse_field_mask("rule,text")
        output, node_count = self.parse_result(
            output_format="csv",
            include_rules="method_declaration",
            fields=fields,
        )
        text = output.decode("utf-8")

        self.assertEqual(node_count, 1)
        self.assertTrue(text.startswith("rule,text\n"))
        self.assertIn("method_declaration", text)
        self.assertIn("getProgramas", text)

    def test_binary_returns_msgpack_with_raw_text_bytes(self) -> None:
        result = self.tsmp.parse_bytes(
            b"class Demo { // caf\xe9\n  void m() {}\n}\n",
            output_format="binary",
            include_rules=["class_declaration", "method_declaration"],
            fields=["id", "parent_id", "rule", "text", "byte_range"],
        )
        document = unpack_msgpack(result.data)

        self.assertEqual(document["format"], "tsmp-binary")
        self.assertEqual(document["schemaVersion"], 1)
        self.assertEqual(document["language"], "java")
        self.assertEqual(document["nodeCount"], result.node_count)
        self.assertEqual([node["rule"] for node in document["nodes"]], ["class_declaration", "method_declaration"])
        self.assertIsInstance(document["nodes"][0]["text"], bytes)
        self.assertIn(b"caf\xe9", document["nodes"][0]["text"])
        self.assertIn("startByte", document["nodes"][0])

    def test_binary_document_decodes_to_structured_python_objects(self) -> None:
        result = self.tsmp.parse_bytes(
            b"class Demo { // caf\xe9\n  void m() {}\n}\n",
            ParseOptions(
                output_format=OutputFormat.BINARY,
                include_rules=["class_declaration", "method_declaration"],
                fields=Field.ID | Field.PARENT_ID | Field.RULE | Field.TEXT | Field.BYTE_RANGE,
            ),
        )
        document = result.binary_document()
        also_document = decode_binary(result.data)

        self.assertEqual(document.format, "tsmp-binary")
        self.assertEqual(document.schema_version, 1)
        self.assertEqual(document.language, "java")
        self.assertEqual(document.node_count, result.node_count)
        self.assertEqual([node.rule for node in document.nodes], ["class_declaration", "method_declaration"])
        self.assertIn(b"caf\xe9", document.nodes[0].text or b"")
        self.assertEqual(also_document.nodes[1].rule, "method_declaration")

    def test_binary_summary_reports_length_without_copy(self) -> None:
        full = self.tsmp.parse_bytes(
            self.source,
            output_format="binary",
            include_rules=["method_declaration"],
            fields=["rule", "text"],
        )
        summary = self.tsmp.parse_bytes_summary(
            self.source,
            output_format="binary",
            include_rules=["method_declaration"],
            fields=["rule", "text"],
        )

        self.assertEqual(summary.output_format, "binary")
        self.assertEqual(summary.node_count, full.node_count)
        self.assertEqual(summary.output_length, len(full.data))

    def test_json_diagnostics_reports_tree_sitter_errors(self) -> None:
        result = self.tsmp.parse_bytes(
            b"class Demo { void broken( { }",
            output_format="json",
            fields=["rule", "diagnostics", "range", "byte_range"],
        )
        document = result.json()

        self.assertTrue(document["hasErrors"])
        self.assertGreater(document["errorNodeCount"], 0)
        self.assertIn("missingNodeCount", document)
        self.assertIn("errorByteCount", document)
        self.assertTrue(any(node["hasError"] for node in document["nodes"]))
        self.assertTrue(any("isError" in node and "isMissing" in node for node in document["nodes"]))
        self.assertIn("startLine", document["nodes"][0])
        self.assertIn("startByte", document["nodes"][0])

    def test_csv_diagnostics_adds_flat_error_columns(self) -> None:
        result = self.tsmp.parse_bytes(
            b"class Demo { void broken( { }",
            output_format="csv",
            fields=["rule", "diagnostics"],
        )
        text = result.data.decode("utf-8")

        self.assertTrue(text.startswith("rule,is_error,is_missing,has_error\n"))
        self.assertIn(",1", text)

    def test_binary_diagnostics_decodes_error_fields(self) -> None:
        result = self.tsmp.parse_bytes(
            b"class Demo { void broken( { }",
            output_format="binary",
            fields=["rule", "diagnostics"],
        )
        document = unpack_msgpack(result.data)

        self.assertTrue(document["hasErrors"])
        self.assertGreater(document["errorNodeCount"], 0)
        self.assertIn("missingNodeCount", document)
        self.assertIn("errorByteCount", document)
        self.assertTrue(any(node["hasError"] for node in document["nodes"]))
        self.assertTrue(all("isError" in node and "isMissing" in node for node in document["nodes"]))

    def test_diagnostics_format_returns_small_quality_payload(self) -> None:
        result = self.tsmp.parse_bytes(
            b"class Demo { void broken( { }",
            output_format="diagnostics",
        )
        document = result.json()

        self.assertEqual(result.output_format, "diagnostics")
        self.assertEqual(document["language"], "java")
        self.assertEqual(document["nodeCount"], result.node_count)
        self.assertTrue(document["hasErrors"])
        self.assertGreater(document["errorNodeCount"], 0)
        self.assertIn("missingNodeCount", document)
        self.assertIn("errorByteCount", document)
        self.assertNotIn("nodes", document)
        self.assertLess(len(result.data), 160)

    def test_stats_counts_without_output(self) -> None:
        output, node_count = self.parse_result(output_format="stats", include_rules="")

        self.assertEqual(output, b"")
        self.assertEqual(node_count, 100)

    def test_invalid_language_returns_error(self) -> None:
        with self.assertRaises(NativeParseError):
            self.tsmp.parse_result(self.source, language="missing", output_format="stats")

    def test_load_language_extension_by_path(self) -> None:
        extension_path = test_language_extension_path()
        self.assertTrue(extension_path.exists(), extension_path)

        parser = Tsmp(default_library_path())
        self.assertFalse(parser.language_available("java_extension"))
        load_result = parser.load_language_extension(extension_path)
        self.assertEqual(load_result.language, "java_extension")
        self.assertEqual(load_result.display_name, "Java Test Extension")
        self.assertTrue(parser.language_available("java_extension"))

        result = parser.parse_text(
            "class Demo { void run() {} }",
            language="java_extension",
            output_format="json",
            include_rules=["method_declaration"],
            fields=["rule", "text"],
        )
        document = result.json()
        self.assertEqual(result.node_count, 1)
        self.assertEqual(document["language"], "java_extension")
        self.assertEqual(document["nodes"][0]["rule"], "method_declaration")

    def test_cobol_auto_safe_normalization_removes_legacy_trailer(self) -> None:
        extension_path = cobol_language_extension_path()
        if not extension_path.exists():
            self.skipTest(f"COBOL extension is not built: {extension_path}")

        parser = Tsmp(default_library_path())
        load_cobol_extension(parser, extension_path)
        source = (
            b"       IDENTIFICATION DIVISION.\n"
            b"       PROGRAM-ID. DEMO.\n"
            b"FHA\n"
            b"\x1a"
        )

        result = parser.parse_bytes(
            source,
            language="cobol",
            output_format="json",
            fields=["rule", "text", "byte_range"],
        )

        self.assertGreater(result.node_count, 0)
        self.assertNotIn(b"FHA", result.data)
        self.assertNotIn(b"\\u001a", result.data)

    def test_cobol_auto_safe_normalization_handles_fixed_layout_view_repairs(self) -> None:
        extension_path = cobol_language_extension_path()
        if not extension_path.exists():
            self.skipTest(f"COBOL extension is not built: {extension_path}")

        parser = Tsmp(default_library_path())
        load_cobol_extension(parser, extension_path)
        sources = {
            "left_shifted_program": (
                b" IDENTIFICATION DIVISION.\n"
                b" PROGRAM-ID. KNORRBK.\n"
                b" DATA DIVISION.\n"
                b" WORKING-STORAGE SECTION.\n"
                b" 01 WS-A PIC X.\n"
                b" PROCEDURE DIVISION.\n"
                b"     GOBACK.\n"
            ),
            "perform_thru_before_paragraph": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. PCL.\n"
                b"       PROCEDURE DIVISION.\n"
                b"       INICIO-PROGRAMA.\n"
                b"           PERFORM 000-TELA        THRU 000-SAI\n"
                b"      *\n"
                b"       010-INICIALIZACAO.\n"
                b"           GOBACK.\n"
                b"       000-TELA.\n"
                b"           EXIT.\n"
                b"       000-SAI.\n"
                b"           EXIT.\n"
            ),
            "continuation_to_target": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. VCP.\n"
                b"       DATA DIVISION.\n"
                b"       WORKING-STORAGE SECTION.\n"
                b"       01 MSGTXT PIC X(80).\n"
                b"       PROCEDURE DIVISION.\n"
                b"           IF MSGTXT = SPACES THEN\n"
                b"              MOVE 'IDENTIFICADOR (,991) NAO FOI INFORMADO'\n"
                b"      -                             TO MSGTXT\n"
                b"           ELSE\n"
                b"              GOBACK.\n"
            ),
            "continuation_string_literal": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. STR.\n"
                b"       DATA DIVISION.\n"
                b"       WORKING-STORAGE SECTION.\n"
                b"       01 TEXTO PIC X(80).\n"
                b"       PROCEDURE DIVISION.\n"
                b"           MOVE \"LC;PROD;DESCRICAO DO PRODUTO;HOR.C\"\n"
                b"      -    \"RIA;\"\n"
                b"           TO TEXTO.\n"
                b"           GOBACK.\n"
            ),
            "display_before_paragraph": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. DSP.\n"
                b"       PROCEDURE DIVISION.\n"
                b"       000-TELA.\n"
                b"           DISPLAY \"MENU\" AT 0101\n"
                b"       000-SAI.\n"
                b"           GOBACK.\n"
            ),
            "display_continuation_before_inline_exit_paragraph": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. DS2.\n"
                b"       PROCEDURE DIVISION.\n"
                b"       001-TELA.\n"
                b"           DISPLAY \"Cliente -> < .. >\" AT 0904\n"
                b"                   \"Periodo -> < .. .. .... >\" AT 1104\n"
                b"       001-FIM. EXIT.\n"
                b"       900-FINALIZACAO.\n"
                b"           GOBACK.\n"
            ),
            "display_dangling_at_before_statement": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. DAT.\n"
                b"       DATA DIVISION.\n"
                b"       WORKING-STORAGE SECTION.\n"
                b"       01 CHAVE-LANC PIC X(10).\n"
                b"       01 KLIDO PIC 9(04).\n"
                b"       PROCEDURE DIVISION.\n"
                b"       LEITURA.\n"
                b"           DISPLAY CHAVE-LANC AT\n"
                b"           ADD 1 TO KLIDO\n"
                b"       FIM.\n"
                b"           GOBACK.\n"
            ),
            "display_period_before_at": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. DPA.\n"
                b"       PROCEDURE DIVISION.\n"
                b"       TELA.\n"
                b"           DISPLAY \"operacoes com a Ljas.Americanas:\".       AT 1120.\n"
                b"           GOBACK.\n"
            ),
            "long_display_before_paragraph": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. LD1.\n"
                b"       PROCEDURE DIVISION.\n"
                b"       TELA.\n"
                b"           DISPLAY\n"
                b"           \"A\" AT 0101 WITH REVERSE-VIDEO\n"
                b"           \"B\" AT 0201 WITH REVERSE-VIDEO\n"
                b"           \"C\" AT 0301 WITH REVERSE-VIDEO\n"
                b"           \"D\" AT 0401 WITH REVERSE-VIDEO\n"
                b"       TELA2.\n"
                b"           GOBACK.\n"
            ),
            "read_before_paragraph": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. RED.\n"
                b"       DATA DIVISION.\n"
                b"       FILE SECTION.\n"
                b"       FD ENTRADA.\n"
                b"       01 REG-ENTRADA PIC X(10).\n"
                b"       PROCEDURE DIVISION.\n"
                b"       010-LER.\n"
                b"           READ ENTRADA AT END GO TO 010-FIM\n"
                b"       010-FIM.\n"
                b"           GOBACK.\n"
            ),
            "move_before_paragraph": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. MOV.\n"
                b"       DATA DIVISION.\n"
                b"       WORKING-STORAGE SECTION.\n"
                b"       01 WS-A PIC X(10).\n"
                b"       PROCEDURE DIVISION.\n"
                b"       020-MOVE.\n"
                b"           MOVE SPACES TO WS-A\n"
                b"       020-FIM.\n"
                b"           GOBACK.\n"
            ),
            "split_move_before_paragraph": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. MV2.\n"
                b"       DATA DIVISION.\n"
                b"       WORKING-STORAGE SECTION.\n"
                b"       01 TEXTO PIC X(80).\n"
                b"       PROCEDURE DIVISION.\n"
                b"       CRIA-TEXTO.\n"
                b"           MOVE\n"
                b"           \"LC;PROD;DESCRICAO DO PRODUTO\"\n"
                b"           TO TEXTO\n"
                b"       CRIA-TEXTO-SAI.\n"
                b"           GOBACK.\n"
            ),
            "compute_before_next_compute": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. CMP.\n"
                b"       DATA DIVISION.\n"
                b"       WORKING-STORAGE SECTION.\n"
                b"       01 A PIC 9(9)V99.\n"
                b"       01 B PIC 9(9)V99.\n"
                b"       01 C PIC 9(9)V99.\n"
                b"       PROCEDURE DIVISION.\n"
                b"           COMPUTE A ROUNDED = (B\n"
                b"                   / C) * 2\n"
                b"           COMPUTE B ROUNDED = (A\n"
                b"                   * 0.19) - ((B / C) * 0.12).\n"
                b"           GOBACK.\n"
            ),
            "compute_decimal_comma_continuation": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. CDC.\n"
                b"       DATA DIVISION.\n"
                b"       WORKING-STORAGE SECTION.\n"
                b"       01 WVAL032 PIC 9(9)V99.\n"
                b"       01 VAL001 PIC 9(9)V99.\n"
                b"       01 VAL002 PIC 9(9)V99.\n"
                b"       PROCEDURE DIVISION.\n"
                b"           COMPUTE WVAL032 =\n"
                b"             ((VAL001 * (0,75 + (0,375 *\n"
                b"              ((VAL002 / (VAL001 + 24)) - 24,72)))) +\n"
                b"              (VAL002 * 0,50).\n"
                b"           GOBACK.\n"
            ),
            "abbreviated_not_equal_literal_continuation": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. ALC.\n"
                b"       DATA DIVISION.\n"
                b"       WORKING-STORAGE SECTION.\n"
                b"       01 WTIPO-C PIC X.\n"
                b"       01 K-ERRO PIC X(40).\n"
                b"       PROCEDURE DIVISION.\n"
                b"           IF WTIPO-C NOT = \"B\" AND \"R\" AND \"H\" AND \"L\" AND \"P\"\n"
                b"                            \"S\" AND \"E\" AND \"X\" AND \"T\" AND \"C\"\n"
                b"                            \"Q\" AND \"A\" AND \"O\" AND \"F\" AND \"I\"\n"
                b"              MOVE \" Tipo Mercado Invalido Verifique\" TO K-ERRO.\n"
                b"           GOBACK.\n"
            ),
            "if_missing_close_paren_before_statement": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. ICP.\n"
                b"       DATA DIVISION.\n"
                b"       WORKING-STORAGE SECTION.\n"
                b"       01 WS-DIA-PRDF PIC 9(02).\n"
                b"       01 WS-MES-PRDF PIC 9(02).\n"
                b"       01 WS-RESTO-02 PIC 9(02).\n"
                b"       PROCEDURE DIVISION.\n"
                b"           IF (WS-DIA-PRDF > 28 AND (WS-MES-PRDF = 2 AND WS-RESTO-02 >\n"
                b"                                     0)\n"
                b"           OR (WS-DIA-PRDF > 29 AND (WS-MES-PRDF = 2 AND WS-RESTO-02 =\n"
                b"                                     0)\n"
                b"              MOVE 1 TO WS-DIA-PRDF.\n"
                b"           GOBACK.\n"
            ),
            "display_terminator_in_column_73_before_paragraph": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. D73.\n"
                b"       PROCEDURE DIVISION.\n"
                b"       TELA.\n"
                b"           DISPLAY \"       <F5> P/ELIMINAR REG.                \" AT 2115.\n"
                b"       TELA2.\n"
                b"           GOBACK.\n"
            ),
            "procedure_copybook_fragment_starts_with_paragraph": (
                b"       INICIO-E0.\n"
                b"           CALL \"PPREV112\" USING WLK-CDLOC WLK-DSEMP WLK-DSLOC.\n"
                b"           CANCEL \"PPREV112\".\n"
                b"           IF WS-QUEST EQUAL 1\n"
                b"              GO INICIO-E0-SAI.\n"
                b"       INICIO-E0-SAI.\n"
                b"           EXIT.\n"
            ),
            "alphanumeric_sequence_area": (
                b"PEDROF IDENTIFICATION DIVISION.\n"
                b"PEDROF PROGRAM-ID. SEQ.\n"
                b"PEDROF PROCEDURE DIVISION.\n"
                b"PEDROF 100000-INICIO.\n"
                b"PEDROF     DISPLAY \"OK\" AT 0101\n"
                b"PEDROF 100000-FIM. EXIT.\n"
                b"       900000-FINAL.\n"
                b"           GOBACK.\n"
            ),
            "else_bare_label_go": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. ELS.\n"
                b"       PROCEDURE DIVISION.\n"
                b"       INICIO.\n"
                b"           IF WS-A = \"08\"\n"
                b"              GO PESQ-OM01\n"
                b"              ELSE\n"
                b"              ROT-LER.\n"
                b"       PESQ-OM01.\n"
                b"           GOBACK.\n"
                b"       ROT-LER.\n"
                b"           GOBACK.\n"
            ),
            "leading_level_prefix_digit": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. LVL.\n"
                b"       DATA DIVISION.\n"
                b"       WORKING-STORAGE SECTION.\n"
                b"       01 DETALHE.\n"
                b"       8    03 FILLER PIC X(50) VALUE \"A\".\n"
                b"       1         88 FLAG-ON VALUE B\"1\".\n"
                b"       PROCEDURE DIVISION.\n"
                b"           GOBACK.\n"
            ),
            "move_trailing_to_before_paragraph": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. MTO.\n"
                b"       PROCEDURE DIVISION.\n"
                b"       GRAVA-NFISCAL.\n"
                b"           MOVE ZEROS TO CFOPCODE MOVE \"I\" TO INSTRUCAO.\n"
                b"           MOVE \"N\" TO SITUACAO MOVE CNPJEDI TO\n"
                b"\n"
                b"       ACESSA-MF030.\n"
                b"           GOBACK.\n"
            ),
            "compute_missing_close_paren_before_end_if": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. CPE.\n"
                b"       PROCEDURE DIVISION.\n"
                b"           IF WK-VLIPI = ZEROS\n"
                b"              MOVE ZEROS TO WS-QTDTOTTRIB\n"
                b"             ELSE\n"
                b"              COMPUTE WS-VLUNITRIB = ((WK-VLIPI / WK-QTDE)\n"
                b"                                           * 10000)\n"
                b"           END-IF.\n"
                b"           GOBACK.\n"
            ),
            "change_marker_continuation_if_or": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. CMO.\n"
                b"       PROCEDURE DIVISION.\n"
                b"           IF STIPMAQ OF TELA01-O < 1   OR\n"
                b"*1            STIPMAQ OF TELA01-O > 3\n"
                b"              MOVE \"TIPO DE MAQUINA INVALIDO\" TO SMSG\n"
                b"              SET IN31-OFF TO TRUE\n"
                b"              GO TO 020-VALIDA-TELA1.\n"
                b"           GOBACK.\n"
            ),
            "display_fixed_suffix_after_period": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. DSA.\n"
                b"       PROCEDURE DIVISION.\n"
                b"           DISPLAY \"          lista   ->< ...... > \"          AT 1120.  AT 1620.\n"
                b"      *\n"
                b"       FINALIZACAO.\n"
                b"           GOBACK.\n"
            ),
            "compute_continuation_after_prior_if": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. CCP.\n"
                b"       PROCEDURE DIVISION.\n"
                b"           IF WS-OPC = \"S\"\n"
                b"              MOVE 1 TO WS-FLAG.\n"
                b"           COMPUTE WQTMETA ROUNDED =\n"
                b"                   ((QTMETA OF DBURN139 / WDIASUT) * DTDIAS).\n"
                b"           COMPUTE WS-PERC01 ROUNDED =\n"
                b"                   ((QTVENDA OF DBURN139 / WQTMETA) * 100).\n"
                b"           GOBACK.\n"
            ),
            "trailing_sequence_digit_after_move": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. TSD.\n"
                b"       PROCEDURE DIVISION.\n"
                b"           MOVE NMBAIRRO OF R-DVASI01L18 TO RCDBAIR3                   2\n"
                b"           MOVE NMCID OF R-DVASI01L18   TO RCDCID3\n"
                b"           GOBACK.\n"
            ),
            "trailing_alphanumeric_sequence_after_move": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. TSA.\n"
                b"       PROCEDURE DIVISION.\n"
                b"           MOVE SERNUM OF REG-DEC001L1  TO RSERIE3                     1T2\n"
                b"           MOVE MOD    OF REG-DEC001L1  TO RMODELO\n"
                b"           GOBACK.\n"
            ),
            "star_banner_marker_in_if_continuation": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. SBM.\n"
                b"       PROCEDURE DIVISION.\n"
                b"           IF NFDTPRESCT OF MF024CFR16 NOT = WS-DATA0 OR\n"
                b"    LU************* (NFDTPRESCT OF MF024CFR16 = WS-DATA0 AND\n"
                b"                    NFSTATUS OF MF024CFR16 EQUAL \"U\"\n"
                b"              WRITE REG-DGRID001\n"
                b"              GO 065-ACESSA-CONT\n"
                b"           END-IF.\n"
                b"           GOBACK.\n"
            ),
            "move_continuation_inline_write": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. MIW.\n"
                b"       PROCEDURE DIVISION.\n"
                b"           MOVE\n"
                b"           \"LC;PROD;DESCRICAO DO PRODUTO;QUANTID;DT.MOVTO;DAT.CRIA;HOR.C\"\n"
                b"      -    \"RIA;\"\n"
                b"           TO TEXTO WRITE REG-PEDPENDPR.\n"
                b"           GOBACK.\n"
            ),
            "start_key_continuation_in_area_a": (
                b"       IDENTIFICATION DIVISION.\n"
                b"       PROGRAM-ID. SKC.\n"
                b"       PROCEDURE DIVISION.\n"
                b"           START DPREV412 KEY IS NOT LESS THAN\n"
                b"       KEY-DPREV412.\n"
                b"           IF W-STAT NOT EQUAL \"00\"\n"
                b"              GO TO 200-FIM\n"
                b"           END-IF.\n"
                b"           GOBACK.\n"
            ),
        }

        for name, source in sources.items():
            with self.subTest(name=name):
                result = parser.parse_bytes(
                    source,
                    language="cobol",
                    output_format="diagnostics",
                    normalization="auto_safe",
                )
                document = result.json()
                self.assertFalse(document["hasErrors"])
                self.assertEqual(document["errorNodeCount"], 0)
                self.assertEqual(document["missingNodeCount"], 0)

    def test_cobol_normalization_can_be_disabled(self) -> None:
        extension_path = cobol_language_extension_path()
        if not extension_path.exists():
            self.skipTest(f"COBOL extension is not built: {extension_path}")

        parser = Tsmp(default_library_path())
        load_cobol_extension(parser, extension_path)
        source = (
            b"\xef\xbb\xbf"
            b"       IDENTIFICATION DIVISION.\n"
            b"       PROGRAM-ID. DEMO.\n"
        )

        result = parser.parse_bytes(
            source,
            language="cobol",
            output_format="json",
            fields=["rule", "text", "byte_range"],
            normalization="none",
        )

        self.assertGreater(result.node_count, 0)

    def test_python_language_extension_parses_json_binary_and_diagnostics(self) -> None:
        extension_path = python_language_extension_path()
        if not extension_path.exists():
            self.skipTest(f"Python extension is not built: {extension_path}")

        parser = Tsmp(default_library_path())
        if not parser.language_available("python"):
            load_result = parser.load_language_extension(extension_path)
            self.assertEqual(load_result.language, "python")
            self.assertEqual(load_result.display_name, "Python")
        self.assertTrue(parser.language_available("python"))

        source = (
            b"import os\n\n"
            b"class Demo:\n"
            b"    def run(self, value: int) -> int:\n"
            b"        return value + 1\n"
        )
        json_result = parser.parse_bytes(
            source,
            ParseOptions(
                language="python",
                output_format=OutputFormat.JSON,
                include_rules=["import_statement", "class_definition", "function_definition"],
                fields=Field.RULE | Field.TEXT | Field.RANGE | Field.BYTE_RANGE | Field.DIAGNOSTICS,
            ),
        )
        json_document = json_result.json()
        self.assertFalse(json_document["hasErrors"])
        self.assertEqual(
            [node["rule"] for node in json_document["nodes"]],
            ["import_statement", "class_definition", "function_definition"],
        )
        self.assertIn("startLine", json_document["nodes"][0])
        self.assertIn("startByte", json_document["nodes"][0])

        binary_result = parser.parse_bytes(
            source,
            ParseOptions(
                language="python",
                output_format=OutputFormat.BINARY,
                include_rules=["class_definition", "function_definition"],
                fields=Field.RULE | Field.TEXT | Field.BYTE_RANGE,
            ),
        )
        binary_document = binary_result.binary_document()
        self.assertEqual([node.rule for node in binary_document.nodes], ["class_definition", "function_definition"])

        diagnostics = parser.parse_bytes(
            b"def broken(:\n    pass\n",
            ParseOptions(language="python", output_format=OutputFormat.DIAGNOSTICS),
        ).json()
        self.assertTrue(diagnostics["hasErrors"])
        self.assertGreater(diagnostics["missingNodeCount"], 0)

    def test_rust_language_extension_parses_json_binary_and_diagnostics(self) -> None:
        extension_path = rust_language_extension_path()
        if not extension_path.exists():
            self.skipTest(f"Rust extension is not built: {extension_path}")

        parser = Tsmp(default_library_path())
        if not parser.language_available("rust"):
            load_result = parser.load_language_extension(extension_path)
            self.assertEqual(load_result.language, "rust")
            self.assertEqual(load_result.display_name, "Rust")
        self.assertTrue(parser.language_available("rust"))

        source = (
            b"use std::fmt;\n\n"
            b"struct Demo { value: i32 }\n\n"
            b"fn run(value: i32) -> i32 {\n"
            b"    value + 1\n"
            b"}\n"
        )
        json_result = parser.parse_bytes(
            source,
            ParseOptions(
                language="rust",
                output_format=OutputFormat.JSON,
                include_rules=["use_declaration", "struct_item", "function_item"],
                fields=Field.RULE | Field.TEXT | Field.RANGE | Field.BYTE_RANGE | Field.DIAGNOSTICS,
            ),
        )
        json_document = json_result.json()
        self.assertFalse(json_document["hasErrors"])
        self.assertEqual(
            [node["rule"] for node in json_document["nodes"]],
            ["use_declaration", "struct_item", "function_item"],
        )

        binary_result = parser.parse_bytes(
            source,
            ParseOptions(
                language="rust",
                output_format=OutputFormat.BINARY,
                include_rules=["struct_item", "function_item"],
                fields=Field.RULE | Field.TEXT | Field.BYTE_RANGE,
            ),
        )
        binary_document = binary_result.binary_document()
        self.assertEqual([node.rule for node in binary_document.nodes], ["struct_item", "function_item"])

        diagnostics = parser.parse_bytes(
            b"fn broken( {\n",
            ParseOptions(language="rust", output_format=OutputFormat.DIAGNOSTICS),
        ).json()
        self.assertTrue(diagnostics["hasErrors"])

    def test_empty_source_is_valid(self) -> None:
        output, node_count = self.tsmp.parse_result(b"", language="java", output_format="json")
        document = json.loads(output)

        self.assertEqual(document["language"], "java")
        self.assertEqual(document["nodeCount"], node_count)
        self.assertGreaterEqual(node_count, 1)
        self.assertEqual(document["nodes"][0]["rule"], "program")

    def test_json_escapes_non_utf8_source_bytes(self) -> None:
        source = b"class Demo { // caf\xe9\n  void m() {}\n}\n"
        output, node_count = self.tsmp.parse_result(source, language="java", output_format="json")
        document = json.loads(output)

        self.assertGreater(node_count, 0)
        self.assertIn(b"\\u00e9", output)
        self.assertEqual(document["nodes"][0]["rule"], "program")

    def test_python_binding_preserves_bytes_after_nul(self) -> None:
        source = b"class Before {}\x00class After {}\n"
        result = self.tsmp.parse_bytes(
            source,
            output_format="json",
            fields=["rule", "text", "byte_range"],
        )

        self.assertIn(b"After", result.data)

    def test_parallel_calls_are_consistent(self) -> None:
        def parse_once() -> int:
            _output, count = self.parse_result(output_format="stats", include_rules="")
            return count

        with ThreadPoolExecutor(max_workers=8) as pool:
            counts = list(pool.map(lambda _: parse_once(), range(32)))

        self.assertEqual(counts, [100] * 32)


if __name__ == "__main__":
    unittest.main()
