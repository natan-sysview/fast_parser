#!/usr/bin/env python3
"""Generate the optional, sidecar FastParse grammar introspection descriptor.

The descriptor is deliberately derived from Tree-sitter's generated grammar.json.
It is not loaded by FastParse's native parser; package consumers may inspect it on
demand to understand the grammar that produced an extension binary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1
ASCII_CASE_PAIR = re.compile(r"\[([A-Za-z])([A-Za-z])\]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a FastParse grammar introspection descriptor."
    )
    parser.add_argument("--language", required=True)
    parser.add_argument("--extension-version", required=True)
    parser.add_argument("--grammar-dir", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def canonical_language(language: str) -> str:
    return language.strip().lower().replace("_", "-")


def default_grammar_dir(language: str) -> Path:
    return ROOT / "grammars" / f"tree-sitter-{canonical_language(language)}"


def default_manifest(language: str) -> Path:
    return ROOT / "extensions" / canonical_language(language) / "manifest.json"


def grammar_hash(grammar_bytes: bytes) -> str:
    return hashlib.sha256(grammar_bytes).hexdigest()


def regex_case_policy(pattern: str) -> tuple[str, str | None]:
    """Return a conservative case policy and canonical literal when provable.

    Tree-sitter grammar JSON stores JS regex source. We only label a regex as
    ASCII case-insensitive when every ASCII letter belongs to an exact [aA] pair.
    Anything more elaborate remains intentionally unknown.
    """

    canonical_parts: list[str] = []
    has_regex_operator = False
    cursor = 0
    for match in ASCII_CASE_PAIR.finditer(pattern):
        first, second = match.groups()
        if first.lower() != second.lower() or first == second:
            return "unknown", None
        residual = pattern[cursor:match.start()]
        if any(char.isascii() and char.isalpha() for char in residual):
            return "unknown", None
        if any(char in r"\\^$.*+?()[]{}|" for char in residual):
            has_regex_operator = True
        canonical_parts.append(residual)
        canonical_parts.append(first.upper())
        cursor = match.end()
    residual = pattern[cursor:]
    if not canonical_parts or any(char.isascii() and char.isalpha() for char in residual):
        return "unknown", None
    if any(char in r"\\^$.*+?()[]{}|" for char in residual):
        has_regex_operator = True
    canonical_parts.append(residual)
    return "ascii-case-insensitive", None if has_regex_operator else "".join(canonical_parts)


def normalize_node(node: Any) -> Any:
    """Normalize generated grammar nodes without expanding grammar references."""

    if isinstance(node, list):
        return [normalize_node(item) for item in node]
    if not isinstance(node, dict):
        return node

    node_type = node.get("type")
    if not isinstance(node_type, str):
        return {key: normalize_node(value) for key, value in sorted(node.items())}

    result: dict[str, Any] = {"kind": node_type.lower()}
    for key in sorted(node):
        if key == "type":
            continue
        value = node[key]
        if key in {"content", "members"}:
            result[key] = normalize_node(value)
        else:
            result[key] = normalize_node(value)

    if node_type == "STRING":
        result["casePolicy"] = "exact"
        result["literal"] = node.get("value", "")
    elif node_type == "PATTERN":
        policy, canonical = regex_case_policy(str(node.get("value", "")))
        result["casePolicy"] = policy
        result["regex"] = node.get("value", "")
        if canonical is not None:
            result["canonicalLiteral"] = canonical
    return result


def generate_descriptor(
    language: str,
    extension_version: str,
    grammar_dir: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    language = canonical_language(language)
    grammar_dir = grammar_dir.resolve()
    manifest_path = manifest_path.resolve()
    grammar_path = grammar_dir / "src" / "grammar.json"
    if not grammar_path.is_file():
        raise FileNotFoundError(f"generated Tree-sitter grammar not found: {grammar_path}")
    if not manifest_path.is_file():
        raise FileNotFoundError(f"extension manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("extensionKind") != "fastparse-language":
        raise ValueError(f"not a FastParse language manifest: {manifest_path}")
    if canonical_language(str(manifest.get("language", ""))) != language:
        raise ValueError(
            f"manifest language {manifest.get('language')!r} does not match {language!r}"
        )
    expected_dir_name = str(manifest.get("grammar", {}).get("name", ""))
    if expected_dir_name != grammar_dir.name:
        raise ValueError(
            f"manifest grammar {expected_dir_name!r} does not match grammar directory "
            f"{grammar_dir.name!r}"
        )

    grammar_bytes = grammar_path.read_bytes()
    grammar = json.loads(grammar_bytes)
    rules = grammar.get("rules")
    if not isinstance(rules, dict) or not rules:
        raise ValueError(f"Tree-sitter grammar has no rules: {grammar_path}")

    grammar_identity = manifest["grammar"]
    return {
        "format": "fastparse-grammar-introspection",
        "schemaVersion": SCHEMA_VERSION,
        "extension": {
            "language": language,
            "displayName": manifest.get("displayName", language),
            "version": extension_version,
            "extensionAbi": manifest.get("extensionAbi"),
        },
        "grammar": {
            "name": grammar.get("name"),
            "packageName": grammar_identity["name"],
            "source": grammar_identity.get("source"),
            "revision": grammar_identity.get("revision"),
            "license": grammar_identity.get("license"),
            "sourceFile": "src/grammar.json",
            "sha256": grammar_hash(grammar_bytes),
            "word": grammar.get("word"),
            "ruleCount": len(rules),
        },
        "rules": {name: normalize_node(rules[name]) for name in sorted(rules)},
    }


def write_descriptor(descriptor: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(descriptor, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    language = canonical_language(args.language)
    descriptor = generate_descriptor(
        language,
        args.extension_version,
        (args.grammar_dir or default_grammar_dir(language)).resolve(),
        (args.manifest or default_manifest(language)).resolve(),
    )
    write_descriptor(descriptor, args.output.resolve())
    print(f"Grammar introspection descriptor: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
