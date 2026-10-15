"""Contract tests for generated language grammar introspection descriptors."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "generate_grammar_introspection.py"
SPEC = importlib.util.spec_from_file_location("grammar_introspection", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GrammarIntrospectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.grammar_dir = ROOT / "grammars" / "tree-sitter-cobol"
        self.manifest = ROOT / "extensions" / "cobol" / "manifest.json"

    def test_cobol_descriptor_is_deterministic_and_hashes_the_input(self) -> None:
        first = MODULE.generate_descriptor("cobol", "0.1.2-test", self.grammar_dir, self.manifest)
        second = MODULE.generate_descriptor("cobol", "0.1.2-test", self.grammar_dir, self.manifest)
        self.assertEqual(first, second)

        grammar = json.loads((self.grammar_dir / "src" / "grammar.json").read_text(encoding="utf-8"))
        self.assertEqual(first["grammar"]["sha256"], MODULE.grammar_hash(grammar))
        crlf_grammar = json.loads(json.dumps(grammar, indent=2).replace("\n", "\r\n"))
        self.assertEqual(first["grammar"]["sha256"], MODULE.grammar_hash(crlf_grammar))
        self.assertEqual(first["extension"]["language"], "cobol")
        self.assertEqual(first["extension"]["version"], "0.1.2-test")

        with tempfile.TemporaryDirectory() as raw_temp:
            first_path = Path(raw_temp) / "one.json"
            second_path = Path(raw_temp) / "two.json"
            MODULE.write_descriptor(first, first_path)
            MODULE.write_descriptor(second, second_path)
            self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
            self.assertEqual(json.loads(first_path.read_text(encoding="utf-8")), first)

    def test_move_preserves_structure_and_case_policy_without_expansion(self) -> None:
        descriptor = MODULE.generate_descriptor("cobol", "0.1.2-test", self.grammar_dir, self.manifest)
        move = descriptor["rules"]["move_statement"]
        self.assertEqual(move["kind"], "seq")
        self.assertEqual(move["members"][0]["kind"], "symbol")
        self.assertEqual(move["members"][0]["name"], "_MOVE")
        self.assertEqual(move["members"][1]["kind"], "choice")

        move_keyword = descriptor["rules"]["_MOVE"]
        self.assertEqual(move_keyword["kind"], "pattern")
        self.assertEqual(move_keyword["casePolicy"], "ascii-case-insensitive")
        self.assertEqual(move_keyword["canonicalLiteral"], "MOVE")

        corresponding = descriptor["rules"]["_CORRESPONDING"]
        self.assertEqual(corresponding["casePolicy"], "ascii-case-insensitive")
        self.assertNotIn("canonicalLiteral", corresponding)
        self.assertIn("?", corresponding["regex"])

        target_list = descriptor["rules"]["_target_x_list"]
        self.assertEqual(target_list["kind"], "repeat1")
        self.assertEqual(target_list["content"]["kind"], "symbol")

    def test_wrong_grammar_directory_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.generate_descriptor(
                "cobol",
                "0.1.2-test",
                ROOT / "grammars" / "tree-sitter-python",
                self.manifest,
            )


if __name__ == "__main__":
    unittest.main()
