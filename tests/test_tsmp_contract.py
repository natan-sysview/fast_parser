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
from tsmp import NativeParseError, Tsmp, default_library_path, parse_field_mask  # noqa: E402


SOURCE_PATH = ROOT / "file_test" / "java" / "HelloWorld.java"


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

    def test_stats_counts_without_output(self) -> None:
        output, node_count = self.parse_result(output_format="stats", include_rules="")

        self.assertEqual(output, b"")
        self.assertEqual(node_count, 100)

    def test_invalid_language_returns_error(self) -> None:
        with self.assertRaises(NativeParseError):
            self.tsmp.parse_result(self.source, language="missing", output_format="stats")

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
