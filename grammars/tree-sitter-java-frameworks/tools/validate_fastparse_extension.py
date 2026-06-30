#!/usr/bin/env python3
"""Validate the Java Frameworks grammar through the local FastParse extension."""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


GRAMMAR_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(LAB_ROOT / "bindings" / "python"))

from fastparse import FastParse  # noqa: E402


LANGUAGE = "java-frameworks"
DEFAULT_INVENTORY_DB = LAB_ROOT / "inventory" / "parser_lab_inventory.sqlite"
DEFAULT_OUTPUT_DB = GRAMMAR_ROOT / "runs" / "java_frameworks_fastparse_validation.sqlite"
DEFAULT_REPORT = GRAMMAR_ROOT / "audits" / "java_frameworks_fastparse_extension_validation.md"
DEFAULT_QUERY = LAB_ROOT / "extensions" / "java-frameworks" / "queries" / "frameworks.scm"
DEFAULT_LIBRARY = LAB_ROOT / "bin" / (
    "libfastparse.dylib" if sys.platform == "darwin" else "fastparse.dll" if sys.platform == "win32" else "libfastparse.so"
)
DEFAULT_EXTENSION = LAB_ROOT / "bin" / (
    "libfastparse_language_java_frameworks.dylib"
    if sys.platform == "darwin"
    else "fastparse_language_java_frameworks.dll"
    if sys.platform == "win32"
    else "libfastparse_language_java_frameworks.so"
)

THREAD_LOCAL = threading.local()


@dataclass(frozen=True)
class InventoryFile:
    id: int
    source_root: str
    project_id: int
    project_name: str
    name: str
    absolute_path: str
    source_relative_path: str
    project_relative_path: str
    subtype: str
    package_name: str
    primary_symbol: str
    size_bytes: int
    line_count: int
    sha256: str


@dataclass(frozen=True)
class BinaryDiagnostics:
    language: str
    node_count: int
    has_errors: bool
    error_node_count: int
    missing_node_count: int
    error_byte_count: int


@dataclass(frozen=True)
class ParseSuccess:
    item: InventoryFile
    diagnostics: BinaryDiagnostics
    native_node_count: int
    messagepack_bytes: int
    source_encoding: str
    normalized: bool
    encoding_normalized: bool
    line_ending_normalized: bool
    query_capture_count: int
    query_output_bytes: int
    query_error: str
    elapsed_ms: float


@dataclass(frozen=True)
class ParseFailure:
    item: InventoryFile
    elapsed_ms: float
    error: str


class MessagePackReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0

    def read_byte(self) -> int:
        if self.pos >= len(self.data):
            raise ValueError("unexpected end of MessagePack data")
        value = self.data[self.pos]
        self.pos += 1
        return value

    def read_exact(self, size: int) -> bytes:
        end = self.pos + size
        if end > len(self.data):
            raise ValueError("unexpected end of MessagePack data")
        value = self.data[self.pos:end]
        self.pos = end
        return value

    def skip_exact(self, size: int) -> None:
        end = self.pos + size
        if end > len(self.data):
            raise ValueError("unexpected end of MessagePack data")
        self.pos = end

    def read_uint_be(self, size: int) -> int:
        return int.from_bytes(self.read_exact(size), "big")

    def read_uint(self) -> int:
        prefix = self.read_byte()
        if prefix <= 0x7F:
            return prefix
        if prefix == 0xCC:
            return self.read_uint_be(1)
        if prefix == 0xCD:
            return self.read_uint_be(2)
        if prefix == 0xCE:
            return self.read_uint_be(4)
        if prefix == 0xCF:
            return self.read_uint_be(8)
        raise ValueError(f"expected uint, got MessagePack prefix 0x{prefix:02x}")

    def read_bool(self) -> bool:
        prefix = self.read_byte()
        if prefix == 0xC2:
            return False
        if prefix == 0xC3:
            return True
        raise ValueError(f"expected bool, got MessagePack prefix 0x{prefix:02x}")

    def read_string(self) -> str:
        prefix = self.read_byte()
        if 0xA0 <= prefix <= 0xBF:
            size = prefix & 0x1F
        elif prefix == 0xD9:
            size = self.read_uint_be(1)
        elif prefix == 0xDA:
            size = self.read_uint_be(2)
        elif prefix == 0xDB:
            size = self.read_uint_be(4)
        else:
            raise ValueError(f"expected str, got MessagePack prefix 0x{prefix:02x}")
        return self.read_exact(size).decode("utf-8", errors="replace")

    def read_map_length(self) -> int:
        prefix = self.read_byte()
        if 0x80 <= prefix <= 0x8F:
            return prefix & 0x0F
        if prefix == 0xDE:
            return self.read_uint_be(2)
        if prefix == 0xDF:
            return self.read_uint_be(4)
        raise ValueError(f"expected map, got MessagePack prefix 0x{prefix:02x}")

    def skip_value(self) -> None:
        prefix = self.read_byte()
        if prefix <= 0x7F or 0xE0 <= prefix <= 0xFF or prefix in (0xC0, 0xC2, 0xC3):
            return
        if 0xA0 <= prefix <= 0xBF:
            self.skip_exact(prefix & 0x1F)
            return
        if 0x90 <= prefix <= 0x9F:
            for _ in range(prefix & 0x0F):
                self.skip_value()
            return
        if 0x80 <= prefix <= 0x8F:
            for _ in range(prefix & 0x0F):
                self.skip_value()
                self.skip_value()
            return

        fixed_sizes = {
            0xCC: 1,
            0xCD: 2,
            0xCE: 4,
            0xCF: 8,
            0xD0: 1,
            0xD1: 2,
            0xD2: 4,
            0xD3: 8,
            0xCA: 4,
            0xCB: 8,
        }
        if prefix in fixed_sizes:
            self.skip_exact(fixed_sizes[prefix])
            return
        if prefix in (0xC4, 0xD9):
            self.skip_exact(self.read_uint_be(1))
            return
        if prefix in (0xC5, 0xDA):
            self.skip_exact(self.read_uint_be(2))
            return
        if prefix in (0xC6, 0xDB):
            self.skip_exact(self.read_uint_be(4))
            return
        if prefix == 0xDC:
            for _ in range(self.read_uint_be(2)):
                self.skip_value()
            return
        if prefix == 0xDD:
            for _ in range(self.read_uint_be(4)):
                self.skip_value()
            return
        if prefix == 0xDE:
            for _ in range(self.read_uint_be(2)):
                self.skip_value()
                self.skip_value()
            return
        if prefix == 0xDF:
            for _ in range(self.read_uint_be(4)):
                self.skip_value()
                self.skip_value()
            return
        raise ValueError(f"unsupported MessagePack prefix 0x{prefix:02x}")


def parse_binary_diagnostics(data: bytes) -> BinaryDiagnostics:
    reader = MessagePackReader(data)
    top_count = reader.read_map_length()
    language = ""
    node_count = 0
    has_errors = False
    error_node_count = 0
    missing_node_count = 0
    error_byte_count = 0

    for _ in range(top_count):
        key = reader.read_string()
        if key == "language":
            language = reader.read_string()
        elif key == "nodeCount":
            node_count = reader.read_uint()
        elif key == "hasErrors":
            has_errors = reader.read_bool()
        elif key == "errorNodeCount":
            error_node_count = reader.read_uint()
        elif key == "missingNodeCount":
            missing_node_count = reader.read_uint()
        elif key == "errorByteCount":
            error_byte_count = reader.read_uint()
        else:
            reader.skip_value()

    return BinaryDiagnostics(
        language=language,
        node_count=node_count,
        has_errors=has_errors,
        error_node_count=error_node_count,
        missing_node_count=missing_node_count,
        error_byte_count=error_byte_count,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Java Frameworks files through FastParse.")
    parser.add_argument("--inventory-db", type=Path, default=DEFAULT_INVENTORY_DB)
    parser.add_argument("--out-db", type=Path, default=DEFAULT_OUTPUT_DB)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--query", type=Path, default=DEFAULT_QUERY)
    parser.add_argument("--lib", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--extension", type=Path, default=DEFAULT_EXTENSION)
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--subtype", default="framework")
    parser.add_argument("--progress-every", type=int, default=250)
    return parser.parse_args()


def load_inventory(db_path: Path, *, subtype: str, limit: int) -> list[InventoryFile]:
    where = ["f.type = 'java'"]
    params: list[str] = []
    if subtype and subtype != "all":
        where.append("f.subtype = ?")
        params.append(subtype)
    sql = f"""
        SELECT
            f.id,
            sr.absolute_path AS source_root,
            f.project_id,
            f.project_name,
            f.name,
            f.absolute_path,
            f.source_relative_path,
            f.project_relative_path,
            f.subtype,
            f.package_name,
            f.primary_symbol,
            f.size_bytes,
            f.line_count,
            f.sha256
        FROM files f
        JOIN source_roots sr ON sr.id = f.source_root_id
        WHERE {' AND '.join(where)}
        ORDER BY sr.absolute_path, f.project_name, f.project_relative_path
    """
    if limit > 0:
        sql += f" LIMIT {limit}"

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()

    return [
        InventoryFile(
            id=row["id"],
            source_root=row["source_root"],
            project_id=row["project_id"],
            project_name=row["project_name"],
            name=row["name"],
            absolute_path=row["absolute_path"],
            source_relative_path=row["source_relative_path"],
            project_relative_path=row["project_relative_path"],
            subtype=row["subtype"],
            package_name=row["package_name"],
            primary_symbol=row["primary_symbol"],
            size_bytes=row["size_bytes"],
            line_count=row["line_count"],
            sha256=row["sha256"],
        )
        for row in rows
    ]


def parser_for_thread(library_path: Path, extension_path: Path) -> FastParse:
    parser = getattr(THREAD_LOCAL, "parser", None)
    if parser is None:
        parser = FastParse(library_path)
        if not parser.language_available(LANGUAGE):
            parser.load_language_extension(extension_path)
        THREAD_LOCAL.parser = parser
    return parser


def read_source_for_parse(path: str) -> tuple[bytes, str, bool, bool, bool]:
    raw = Path(path).read_bytes()
    source_encoding = "utf-8"
    encoding_normalized = False
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            source_encoding = encoding
            encoding_normalized = encoding != "utf-8"
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode("latin-1", errors="replace")
        source_encoding = "latin-1-replace"
        encoding_normalized = True

    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
    line_ending_normalized = normalized_text != text
    normalized = encoding_normalized or line_ending_normalized
    return normalized_text.encode("utf-8"), source_encoding, normalized, encoding_normalized, line_ending_normalized


def parse_item(
    item: InventoryFile,
    library_path: Path,
    extension_path: Path,
    query: bytes,
) -> ParseSuccess | ParseFailure:
    started = time.perf_counter()
    try:
        source, source_encoding, normalized, encoding_normalized, line_ending_normalized = read_source_for_parse(item.absolute_path)
        parser = parser_for_thread(library_path, extension_path)
        result = parser.parse_bytes(
            source,
            language=LANGUAGE,
            output_format="binary",
            fields=["rule", "diagnostics"],
            include_tokens=False,
            normalization="none",
        )
        diagnostics = parse_binary_diagnostics(result.data)
        query_capture_count = 0
        query_output_bytes = 0
        query_error = ""
        try:
            query_result = parser.query_bytes_summary(
                source,
                query,
                language=LANGUAGE,
                output_format="stats",
                fields=["capture_name"],
                normalization="none",
            )
            query_capture_count = query_result.node_count
            query_output_bytes = query_result.output_length
        except Exception as exc:  # noqa: BLE001 - query failures must be recorded per file.
            query_error = str(exc)

        elapsed_ms = (time.perf_counter() - started) * 1000
        return ParseSuccess(
            item=item,
            diagnostics=diagnostics,
            native_node_count=result.node_count,
            messagepack_bytes=len(result.data),
            source_encoding=source_encoding,
            normalized=normalized,
            encoding_normalized=encoding_normalized,
            line_ending_normalized=line_ending_normalized,
            query_capture_count=query_capture_count,
            query_output_bytes=query_output_bytes,
            query_error=query_error,
            elapsed_ms=elapsed_ms,
        )
    except Exception as exc:  # noqa: BLE001 - validation must keep file-level failures.
        elapsed_ms = (time.perf_counter() - started) * 1000
        return ParseFailure(item=item, elapsed_ms=elapsed_ms, error=str(exc))


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP VIEW IF EXISTS v_error_files;
        DROP VIEW IF EXISTS v_query_failures;
        DROP TABLE IF EXISTS parse_failures;
        DROP TABLE IF EXISTS parse_results;
        DROP TABLE IF EXISTS validation_runs;

        CREATE TABLE validation_runs (
            id INTEGER PRIMARY KEY,
            generated_at TEXT NOT NULL,
            inventory_db TEXT NOT NULL,
            library_path TEXT NOT NULL,
            extension_path TEXT NOT NULL,
            query_path TEXT NOT NULL,
            language TEXT NOT NULL,
            workers INTEGER NOT NULL,
            file_count INTEGER NOT NULL
        );

        CREATE TABLE parse_results (
            id INTEGER PRIMARY KEY,
            run_id INTEGER NOT NULL REFERENCES validation_runs(id) ON DELETE CASCADE,
            inventory_file_id INTEGER NOT NULL,
            source_root TEXT NOT NULL,
            project_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            name TEXT NOT NULL,
            absolute_path TEXT NOT NULL,
            source_relative_path TEXT NOT NULL,
            project_relative_path TEXT NOT NULL,
            subtype TEXT NOT NULL,
            package_name TEXT NOT NULL,
            primary_symbol TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            line_count INTEGER NOT NULL,
            sha256 TEXT NOT NULL,
            language TEXT NOT NULL,
            native_node_count INTEGER NOT NULL,
            messagepack_node_count INTEGER NOT NULL,
            messagepack_bytes INTEGER NOT NULL,
            source_encoding TEXT NOT NULL,
            normalized INTEGER NOT NULL,
            encoding_normalized INTEGER NOT NULL,
            line_ending_normalized INTEGER NOT NULL,
            elapsed_ms REAL NOT NULL,
            has_errors INTEGER NOT NULL,
            error_node_count INTEGER NOT NULL,
            missing_node_count INTEGER NOT NULL,
            error_byte_count INTEGER NOT NULL,
            query_capture_count INTEGER NOT NULL,
            query_output_bytes INTEGER NOT NULL,
            query_error TEXT NOT NULL
        );

        CREATE TABLE parse_failures (
            id INTEGER PRIMARY KEY,
            run_id INTEGER NOT NULL REFERENCES validation_runs(id) ON DELETE CASCADE,
            inventory_file_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            name TEXT NOT NULL,
            absolute_path TEXT NOT NULL,
            elapsed_ms REAL NOT NULL,
            error TEXT NOT NULL
        );

        CREATE INDEX idx_parse_results_run_id ON parse_results(run_id);
        CREATE INDEX idx_parse_results_has_errors ON parse_results(has_errors);
        CREATE INDEX idx_parse_results_project ON parse_results(project_name);
        CREATE INDEX idx_parse_results_query_capture_count ON parse_results(query_capture_count);
        CREATE INDEX idx_parse_failures_run_id ON parse_failures(run_id);

        CREATE VIEW v_error_files AS
        SELECT
            project_name,
            name,
            absolute_path,
            subtype,
            line_count,
            error_node_count,
            missing_node_count,
            error_byte_count
        FROM parse_results
        WHERE has_errors = 1 OR missing_node_count > 0
        ORDER BY error_byte_count DESC, error_node_count DESC, absolute_path ASC;

        CREATE VIEW v_query_failures AS
        SELECT
            project_name,
            name,
            absolute_path,
            query_error
        FROM parse_results
        WHERE query_error <> ''
        ORDER BY absolute_path ASC;
        """
    )


def write_results(
    db_path: Path,
    *,
    args: argparse.Namespace,
    successes: list[ParseSuccess],
    failures: list[ParseFailure],
    file_count: int,
) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA foreign_keys = ON")
        create_schema(conn)
        cursor = conn.execute(
            """
            INSERT INTO validation_runs(
                generated_at,
                inventory_db,
                library_path,
                extension_path,
                query_path,
                language,
                workers,
                file_count
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                str(args.inventory_db.resolve()),
                str(args.lib.resolve()),
                str(args.extension.resolve()),
                str(args.query.resolve()),
                LANGUAGE,
                args.workers,
                file_count,
            ),
        )
        run_id = cursor.lastrowid

        conn.executemany(
            """
            INSERT INTO parse_results(
                run_id,
                inventory_file_id,
                source_root,
                project_id,
                project_name,
                name,
                absolute_path,
                source_relative_path,
                project_relative_path,
                subtype,
                package_name,
                primary_symbol,
                size_bytes,
                line_count,
                sha256,
                language,
                native_node_count,
                messagepack_node_count,
                messagepack_bytes,
                source_encoding,
                normalized,
                encoding_normalized,
                line_ending_normalized,
                elapsed_ms,
                has_errors,
                error_node_count,
                missing_node_count,
                error_byte_count,
                query_capture_count,
                query_output_bytes,
                query_error
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    result.item.id,
                    result.item.source_root,
                    result.item.project_id,
                    result.item.project_name,
                    result.item.name,
                    result.item.absolute_path,
                    result.item.source_relative_path,
                    result.item.project_relative_path,
                    result.item.subtype,
                    result.item.package_name,
                    result.item.primary_symbol,
                    result.item.size_bytes,
                    result.item.line_count,
                    result.item.sha256,
                    result.diagnostics.language,
                    result.native_node_count,
                    result.diagnostics.node_count,
                    result.messagepack_bytes,
                    result.source_encoding,
                    1 if result.normalized else 0,
                    1 if result.encoding_normalized else 0,
                    1 if result.line_ending_normalized else 0,
                    result.elapsed_ms,
                    1 if result.diagnostics.has_errors else 0,
                    result.diagnostics.error_node_count,
                    result.diagnostics.missing_node_count,
                    result.diagnostics.error_byte_count,
                    result.query_capture_count,
                    result.query_output_bytes,
                    result.query_error,
                )
                for result in successes
            ],
        )

        conn.executemany(
            """
            INSERT INTO parse_failures(
                run_id,
                inventory_file_id,
                project_name,
                name,
                absolute_path,
                elapsed_ms,
                error
            )
            VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    failure.item.id,
                    failure.item.project_name,
                    failure.item.name,
                    failure.item.absolute_path,
                    failure.elapsed_ms,
                    failure.error,
                )
                for failure in failures
            ],
        )
        conn.commit()


def write_report(
    path: Path,
    *,
    args: argparse.Namespace,
    successes: list[ParseSuccess],
    failures: list[ParseFailure],
    elapsed: float,
    file_count: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    error_files = [result for result in successes if result.diagnostics.has_errors]
    missing_files = [result for result in successes if result.diagnostics.missing_node_count > 0]
    query_failures = [result for result in successes if result.query_error]
    capture_files = [result for result in successes if result.query_capture_count > 0]
    normalized_files = [result for result in successes if result.normalized]
    encoding_normalized = [result for result in successes if result.encoding_normalized]
    line_ending_normalized = [result for result in successes if result.line_ending_normalized]

    lines = [
        "# Java Frameworks FastParse Extension Validation",
        "",
        f"Date: {time.strftime('%Y-%m-%dT%H:%M:%S%z')}",
        "",
        "## Inputs",
        "",
        f"- Language: `{LANGUAGE}`",
        f"- Inventory DB: `{args.inventory_db.resolve()}`",
        f"- FastParse library: `{args.lib.resolve()}`",
        f"- Extension: `{args.extension.resolve()}`",
        f"- Query: `{args.query.resolve()}`",
        f"- Output DB: `{args.out_db.resolve()}`",
        f"- Workers: {args.workers}",
        f"- Subtype filter: `{args.subtype}`",
        "",
        "## Summary",
        "",
        f"- Inventory files: {file_count}",
        f"- Parsed OK: {len(successes)}",
        f"- Hard parse failures: {len(failures)}",
        f"- Files with `ERROR`: {len(error_files)}",
        f"- Total `ERROR` nodes: {sum(result.diagnostics.error_node_count for result in successes)}",
        f"- Files with `MISSING`: {len(missing_files)}",
        f"- Total `MISSING` nodes: {sum(result.diagnostics.missing_node_count for result in successes)}",
        f"- Query failures: {len(query_failures)}",
        f"- Files with framework captures: {len(capture_files)}",
        f"- Total framework captures: {sum(result.query_capture_count for result in successes)}",
        f"- FastParse MessagePack bytes: {sum(result.messagepack_bytes for result in successes)}",
        f"- Normalized files: {len(normalized_files)}",
        f"- Encoding-normalized files: {len(encoding_normalized)}",
        f"- Line-ending-normalized files: {len(line_ending_normalized)}",
        f"- Elapsed seconds: {elapsed:.3f}",
        f"- Files/sec: {len(successes) / max(elapsed, 0.001):.1f}",
        "",
        "## Decision",
        "",
    ]

    if failures or error_files or missing_files or query_failures:
        lines.append("Needs investigation before the extension is considered stable.")
    else:
        lines.append("Stable for the current framework inventory through FastParse.")

    if failures:
        lines.extend(["", "## Parse Failure Samples", ""])
        for failure in failures[:10]:
            lines.append(f"- `{failure.item.absolute_path}`: `{failure.error[:300]}`")

    if query_failures:
        lines.extend(["", "## Query Failure Samples", ""])
        for result in query_failures[:10]:
            lines.append(f"- `{result.item.absolute_path}`: `{result.query_error[:300]}`")

    if error_files or missing_files:
        lines.extend(["", "## Error Samples", ""])
        for result in (error_files + missing_files)[:10]:
            lines.append(
                f"- `{result.item.absolute_path}`: errors={result.diagnostics.error_node_count} "
                f"missing={result.diagnostics.missing_node_count}"
            )

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    args.inventory_db = args.inventory_db.resolve()
    args.out_db = args.out_db.resolve()
    args.report_out = args.report_out.resolve()
    args.query = args.query.resolve()
    args.lib = args.lib.resolve()
    args.extension = args.extension.resolve()
    args.workers = max(1, args.workers)

    for path, label in (
        (args.inventory_db, "inventory DB"),
        (args.lib, "FastParse library"),
        (args.extension, "Java Frameworks extension"),
        (args.query, "framework query"),
    ):
        if not path.exists():
            print(f"ERROR: missing {label}: {path}", file=sys.stderr)
            return 2

    inventory = load_inventory(args.inventory_db, subtype=args.subtype, limit=max(0, args.limit))
    if not inventory:
        print("ERROR: no inventory rows matched the requested filters.", file=sys.stderr)
        return 2

    query = args.query.read_bytes()
    probe = FastParse(args.lib)
    print(f"FastParse    : {probe.version}")
    print(f"Inventory DB : {args.inventory_db}")
    print(f"Output DB    : {args.out_db}")
    print(f"Report       : {args.report_out}")
    print(f"Files        : {len(inventory)}")
    print(f"Workers      : {args.workers}")
    print(f"Extension    : {args.extension}")
    if not probe.language_available(LANGUAGE):
        load_result = probe.load_language_extension(args.extension)
        print(f"Loaded       : {load_result.language} ({load_result.display_name})")
    print(f"Available   : {probe.language_available(LANGUAGE)}")

    successes: list[ParseSuccess] = []
    failures: list[ParseFailure] = []
    started = time.perf_counter()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(parse_item, item, args.lib, args.extension, query) for item in inventory]
        for index, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            if isinstance(result, ParseSuccess):
                successes.append(result)
            else:
                failures.append(result)
            if args.progress_every > 0 and index % args.progress_every == 0:
                elapsed_progress = time.perf_counter() - started
                query_failures = sum(1 for item in successes if item.query_error)
                print(
                    f"Progress     : {index}/{len(inventory)} ok={len(successes)} failures={len(failures)} "
                    f"query_failures={query_failures} elapsed={elapsed_progress:.3f}s",
                    flush=True,
                )

    elapsed = time.perf_counter() - started
    successes.sort(key=lambda item: (item.item.source_root, item.item.project_name, item.item.project_relative_path))
    failures.sort(key=lambda item: item.item.absolute_path)
    write_results(args.out_db, args=args, successes=successes, failures=failures, file_count=len(inventory))
    write_report(args.report_out, args=args, successes=successes, failures=failures, elapsed=elapsed, file_count=len(inventory))

    error_files = sum(1 for result in successes if result.diagnostics.has_errors)
    error_nodes = sum(result.diagnostics.error_node_count for result in successes)
    missing_files = sum(1 for result in successes if result.diagnostics.missing_node_count > 0)
    missing_nodes = sum(result.diagnostics.missing_node_count for result in successes)
    query_failures = sum(1 for result in successes if result.query_error)
    capture_files = sum(1 for result in successes if result.query_capture_count > 0)
    normalized_files = sum(1 for result in successes if result.normalized)

    print(f"Parsed OK    : {len(successes)}")
    print(f"Failures     : {len(failures)}")
    print(f"Error files  : {error_files}")
    print(f"Error nodes  : {error_nodes}")
    print(f"Missing files: {missing_files}")
    print(f"Missing nodes: {missing_nodes}")
    print(f"Query failures: {query_failures}")
    print(f"Capture files: {capture_files}")
    print(f"Normalized   : {normalized_files}")
    print(f"Elapsed      : {elapsed:.3f}s")
    print(f"Files/sec    : {len(successes) / max(elapsed, 0.001):.1f}")

    if failures or error_files or missing_files or query_failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
