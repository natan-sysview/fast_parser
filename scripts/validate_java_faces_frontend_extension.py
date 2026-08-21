#!/usr/bin/env python3
"""Load and validate the Java Faces Frontend FastParse extension."""

from __future__ import annotations

import argparse
import os
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bindings" / "python"))

from fastparse import FastParse  # noqa: E402


LANGUAGE = "java-faces-frontend"
THREAD_LOCAL = threading.local()
REQUIRED_RULES = {
    "document",
    "facelets_element",
    "jsf_html_element",
    "jsf_core_element",
    "composite_component_element",
    "faces_element",
    "primefaces_element",
    "primefaces_extensions_element",
    "jstl_element",
    "qualified_element",
    "xml_element",
    "faces_attribute",
    "passthrough_attribute",
    "deferred_expression",
    "immediate_expression",
}
REQUIRED_CAPTURES = {
    "framework.facelets",
    "framework.jsf_html",
    "framework.jsf_core",
    "framework.composite",
    "framework.html_friendly",
    "framework.primefaces",
    "framework.primefaces_extensions",
    "framework.jstl",
    "framework.qualified",
    "framework.xml",
    "attribute.faces",
    "attribute.passthrough",
    "el.deferred",
    "el.immediate",
}


def native_names() -> tuple[str, str]:
    if sys.platform == "darwin":
        return "libfastparse.dylib", "libfastparse_language_java_faces_frontend.dylib"
    if sys.platform == "win32":
        return "fastparse.dll", "fastparse_language_java_faces_frontend.dll"
    return "libfastparse.so", "libfastparse_language_java_faces_frontend.so"


def parse_args() -> argparse.Namespace:
    core_name, extension_name = native_names()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=ROOT / "bin" / core_name)
    parser.add_argument("--extension", type=Path, default=ROOT / "bin" / extension_name)
    parser.add_argument(
        "--sample",
        type=Path,
        default=ROOT / "grammars" / "tree-sitter-java-faces-frontend" / "examples" / "fastparse-smoke.xhtml",
    )
    parser.add_argument(
        "--query",
        type=Path,
        default=ROOT / "extensions" / "java-faces-frontend" / "queries" / "audits.scm",
    )
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--iterations", type=int, default=24)
    return parser.parse_args()


def require_file(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Missing {label}: {resolved}")
    return resolved


def parse_document(parser: FastParse, source: bytes):
    result = parser.parse_bytes(
        source,
        language=LANGUAGE,
        output_format="binary",
        fields=["rule", "diagnostics"],
        include_tokens=False,
        normalization="none",
    )
    document = result.binary_document()
    if document.language != LANGUAGE:
        raise AssertionError(f"Unexpected binary language: {document.language!r}")
    if document.has_errors or document.error_node_count or document.missing_node_count:
        raise AssertionError(
            "Parse diagnostics are not clean: "
            f"has_errors={document.has_errors} "
            f"ERROR={document.error_node_count} MISSING={document.missing_node_count}"
        )
    return result, document


def parser_for_worker(library: Path) -> FastParse:
    parser = getattr(THREAD_LOCAL, "parser", None)
    if parser is None:
        parser = FastParse(library)
        if not parser.language_available(LANGUAGE):
            raise AssertionError(f"{LANGUAGE!r} was not registered before worker startup")
        THREAD_LOCAL.parser = parser
    return parser


def concurrent_parse(library: Path, source: bytes, index: int) -> tuple[int, int]:
    parser = parser_for_worker(library)
    result, document = parse_document(parser, source)
    return index, len(result.data) + document.node_count


def main() -> int:
    args = parse_args()
    library = require_file(args.library, "FastParse core library")
    extension = require_file(args.extension, "Java Faces Frontend extension")
    sample = require_file(args.sample, "Facelets smoke sample")
    query_path = require_file(args.query, "extension audit query")
    source = sample.read_bytes()

    parser = FastParse(library)
    if not parser.language_available(LANGUAGE):
        load_result = parser.load_language_extension(extension)
        if load_result.language != LANGUAGE:
            raise AssertionError(f"Extension registered unexpected language: {load_result.language!r}")
    if not parser.language_available(LANGUAGE):
        raise AssertionError(f"FastParse did not expose {LANGUAGE!r} after extension load")

    result, document = parse_document(parser, source)
    rule_counts = Counter(node.rule for node in document.nodes if node.rule)
    missing_rules = sorted(REQUIRED_RULES - rule_counts.keys())
    if missing_rules:
        raise AssertionError(f"Smoke AST is missing required rules: {missing_rules}")

    query_result = parser.query_bytes(
        source,
        query_path.read_bytes(),
        language=LANGUAGE,
        output_format="json",
        fields=["capture_name", "text"],
        normalization="none",
    )
    query_payload = query_result.json()
    captures = {
        capture.get("name", "")
        for match in query_payload.get("matches", [])
        for capture in match.get("captures", [])
    }
    missing_captures = sorted(REQUIRED_CAPTURES - captures)
    if missing_captures:
        raise AssertionError(f"Audit query is missing required captures: {missing_captures}")

    workers = max(1, args.workers)
    iterations = max(1, args.iterations)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        threaded = list(executor.map(lambda index: concurrent_parse(library, source, index), range(iterations)))
    if len(threaded) != iterations:
        raise AssertionError(f"Expected {iterations} threaded parses, got {len(threaded)}")

    print(f"FastParse version       : {parser.version}")
    print(f"Language                : {LANGUAGE}")
    print(f"Extension               : {extension}")
    print(f"MessagePack bytes       : {len(result.data)}")
    print(f"AST nodes               : {document.node_count}")
    print(f"ERROR nodes             : {document.error_node_count}")
    print(f"MISSING nodes           : {document.missing_node_count}")
    print(f"Query captures          : {query_result.node_count}")
    print(f"Required rules          : {len(REQUIRED_RULES)}/{len(REQUIRED_RULES)}")
    print(f"Required capture groups : {len(REQUIRED_CAPTURES)}/{len(REQUIRED_CAPTURES)}")
    print(f"Concurrent parses       : {len(threaded)} with {workers} workers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
