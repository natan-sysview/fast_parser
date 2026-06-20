#!/usr/bin/env python3
"""Expand persisted FastParse binary ASTs into queryable SQLite node rows."""

from __future__ import annotations

import argparse
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "fastparse_java_ast_binary_threads_fast.sqlite"


@dataclass(frozen=True)
class FileAst:
    parsed_file_id: int
    run_id: int
    inventory_file_id: int
    project_name: str
    absolute_path: str
    file_name: str
    ast_binary: bytes


@dataclass(frozen=True)
class AstNode:
    run_id: int
    parsed_file_id: int
    inventory_file_id: int
    project_name: str
    absolute_path: str
    file_name: str
    node_id: int | None
    parent_id: int | None
    rule: str
    text: str
    text_bytes: int
    start_line: int | None
    start_column: int | None
    end_line: int | None
    end_column: int | None
    start_byte: int | None
    end_byte: int | None
    child_count: int | None
    children_json: str


class MessagePackReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0

    def _read_byte(self) -> int:
        if self.pos >= len(self.data):
            raise ValueError("unexpected end of MessagePack data")
        value = self.data[self.pos]
        self.pos += 1
        return value

    def _read_exact(self, size: int) -> bytes:
        end = self.pos + size
        if end > len(self.data):
            raise ValueError("unexpected end of MessagePack data")
        value = self.data[self.pos:end]
        self.pos = end
        return value

    def _skip_bytes(self, size: int) -> None:
        end = self.pos + size
        if end > len(self.data):
            raise ValueError("unexpected end of MessagePack data")
        self.pos = end

    def _read_uint_be(self, size: int) -> int:
        return int.from_bytes(self._read_exact(size), "big")

    def read_uint(self) -> int:
        prefix = self._read_byte()
        if prefix <= 0x7F:
            return prefix
        if prefix == 0xCC:
            return self._read_uint_be(1)
        if prefix == 0xCD:
            return self._read_uint_be(2)
        if prefix == 0xCE:
            return self._read_uint_be(4)
        if prefix == 0xCF:
            return self._read_uint_be(8)
        raise ValueError(f"expected uint, got MessagePack prefix 0x{prefix:02x}")

    def read_uint_or_nil(self) -> int | None:
        prefix = self._read_byte()
        if prefix == 0xC0:
            return None
        self.pos -= 1
        return self.read_uint()

    def read_str(self) -> str:
        prefix = self._read_byte()
        if 0xA0 <= prefix <= 0xBF:
            size = prefix & 0x1F
        elif prefix == 0xD9:
            size = self._read_uint_be(1)
        elif prefix == 0xDA:
            size = self._read_uint_be(2)
        elif prefix == 0xDB:
            size = self._read_uint_be(4)
        else:
            raise ValueError(f"expected str, got MessagePack prefix 0x{prefix:02x}")
        return self._read_exact(size).decode("utf-8", errors="replace")

    def read_bin(self) -> bytes:
        prefix = self._read_byte()
        if prefix == 0xC4:
            size = self._read_uint_be(1)
        elif prefix == 0xC5:
            size = self._read_uint_be(2)
        elif prefix == 0xC6:
            size = self._read_uint_be(4)
        else:
            raise ValueError(f"expected bin, got MessagePack prefix 0x{prefix:02x}")
        return self._read_exact(size)

    def read_array_len(self) -> int:
        prefix = self._read_byte()
        if 0x90 <= prefix <= 0x9F:
            return prefix & 0x0F
        if prefix == 0xDC:
            return self._read_uint_be(2)
        if prefix == 0xDD:
            return self._read_uint_be(4)
        raise ValueError(f"expected array, got MessagePack prefix 0x{prefix:02x}")

    def read_map_len(self) -> int:
        prefix = self._read_byte()
        if 0x80 <= prefix <= 0x8F:
            return prefix & 0x0F
        if prefix == 0xDE:
            return self._read_uint_be(2)
        if prefix == 0xDF:
            return self._read_uint_be(4)
        raise ValueError(f"expected map, got MessagePack prefix 0x{prefix:02x}")

    def skip_value(self) -> None:
        prefix = self._read_byte()
        if prefix <= 0x7F or 0xE0 <= prefix <= 0xFF or prefix in (0xC0, 0xC2, 0xC3):
            return
        if 0xA0 <= prefix <= 0xBF:
            self._skip_bytes(prefix & 0x1F)
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
        if prefix in (0xCC, 0xD0):
            self._skip_bytes(1)
            return
        if prefix in (0xCD, 0xD1):
            self._skip_bytes(2)
            return
        if prefix in (0xCE, 0xD2):
            self._skip_bytes(4)
            return
        if prefix in (0xCF, 0xD3):
            self._skip_bytes(8)
            return
        if prefix in (0xC4, 0xD9):
            self._skip_bytes(self._read_uint_be(1))
            return
        if prefix in (0xC5, 0xDA):
            self._skip_bytes(self._read_uint_be(2))
            return
        if prefix in (0xC6, 0xDB):
            self._skip_bytes(self._read_uint_be(4))
            return
        if prefix == 0xDC:
            for _ in range(self._read_uint_be(2)):
                self.skip_value()
            return
        if prefix == 0xDD:
            for _ in range(self._read_uint_be(4)):
                self.skip_value()
            return
        if prefix == 0xDE:
            for _ in range(self._read_uint_be(2)):
                self.skip_value()
                self.skip_value()
            return
        if prefix == 0xDF:
            for _ in range(self._read_uint_be(4)):
                self.skip_value()
                self.skip_value()
            return
        raise ValueError(f"unsupported MessagePack prefix 0x{prefix:02x}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Expand FastParse binary AST BLOBs into ast_nodes.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--run-id", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--recreate", action="store_true", help="Drop and rebuild ast_nodes first.")
    parser.add_argument("--progress-every", type=int, default=100)
    return parser.parse_args()


def connect_db(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA cache_size = -262144")
    return conn


def create_schema(conn: sqlite3.Connection, *, recreate: bool) -> None:
    if recreate:
        conn.execute("DROP TABLE IF EXISTS ast_nodes")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS ast_nodes (
            id INTEGER PRIMARY KEY,
            run_id INTEGER NOT NULL,
            parsed_file_id INTEGER NOT NULL REFERENCES parsed_java_files(id) ON DELETE CASCADE,
            inventory_file_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            absolute_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            node_id INTEGER,
            parent_id INTEGER,
            rule TEXT NOT NULL,
            text TEXT NOT NULL,
            text_bytes INTEGER NOT NULL,
            start_line INTEGER,
            start_column INTEGER,
            end_line INTEGER,
            end_column INTEGER,
            start_byte INTEGER,
            end_byte INTEGER,
            child_count INTEGER,
            children_json TEXT NOT NULL
        );
        """
    )


def create_indexes(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_ast_nodes_run_file
            ON ast_nodes(run_id, parsed_file_id);
        CREATE INDEX IF NOT EXISTS idx_ast_nodes_inventory_file
            ON ast_nodes(inventory_file_id);
        CREATE INDEX IF NOT EXISTS idx_ast_nodes_project
            ON ast_nodes(project_name);
        CREATE INDEX IF NOT EXISTS idx_ast_nodes_rule
            ON ast_nodes(rule);
        CREATE INDEX IF NOT EXISTS idx_ast_nodes_parent
            ON ast_nodes(run_id, parsed_file_id, parent_id);
        CREATE INDEX IF NOT EXISTS idx_ast_nodes_range
            ON ast_nodes(run_id, parsed_file_id, start_line, start_column);
        """
    )


def drop_indexes(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP INDEX IF EXISTS idx_ast_nodes_run_file;
        DROP INDEX IF EXISTS idx_ast_nodes_inventory_file;
        DROP INDEX IF EXISTS idx_ast_nodes_project;
        DROP INDEX IF EXISTS idx_ast_nodes_rule;
        DROP INDEX IF EXISTS idx_ast_nodes_parent;
        DROP INDEX IF EXISTS idx_ast_nodes_range;
        """
    )


def count_files(conn: sqlite3.Connection, *, run_id: int, limit: int) -> int:
    if limit > 0:
        return min(
            limit,
            int(
                conn.execute(
                    "SELECT COUNT(*) FROM parsed_java_files WHERE run_id = ?",
                    (run_id,),
                ).fetchone()[0]
            ),
        )
    return int(
        conn.execute(
            "SELECT COUNT(*) FROM parsed_java_files WHERE run_id = ?",
            (run_id,),
        ).fetchone()[0]
    )


def iter_files(conn: sqlite3.Connection, *, run_id: int, limit: int) -> Any:
    query = """
        SELECT
            id,
            run_id,
            inventory_file_id,
            project_name,
            absolute_path,
            file_name,
            ast_binary
        FROM parsed_java_files
        WHERE run_id = ?
        ORDER BY project_name, project_relative_path
    """
    params: list[Any] = [run_id]
    if limit > 0:
        query += " LIMIT ?"
        params.append(limit)
    for row in conn.execute(query, params):
        yield FileAst(
            parsed_file_id=int(row[0]),
            run_id=int(row[1]),
            inventory_file_id=int(row[2]),
            project_name=str(row[3]),
            absolute_path=str(row[4]),
            file_name=str(row[5]),
            ast_binary=bytes(row[6]),
        )


def read_child_summaries(reader: MessagePackReader) -> str:
    children: list[dict[str, Any]] = []
    for _ in range(reader.read_array_len()):
        child: dict[str, Any] = {}
        for _field in range(reader.read_map_len()):
            key = reader.read_str()
            if key == "rule":
                child["rule"] = reader.read_str()
            elif key == "text":
                text = reader.read_bin()
                child["text"] = text.decode("utf-8", errors="replace")
                child["text_bytes"] = len(text)
            else:
                reader.skip_value()
        children.append(child)
    return json.dumps(children, ensure_ascii=True, separators=(",", ":"))


def iter_nodes(file_ast: FileAst) -> Any:
    reader = MessagePackReader(file_ast.ast_binary)
    top_count = reader.read_map_len()

    for _ in range(top_count):
        key = reader.read_str()
        if key != "nodes":
            reader.skip_value()
            continue

        for _node_index in range(reader.read_array_len()):
            node_id: int | None = None
            parent_id: int | None = None
            rule = ""
            text = ""
            text_bytes = 0
            start_line: int | None = None
            start_column: int | None = None
            end_line: int | None = None
            end_column: int | None = None
            start_byte: int | None = None
            end_byte: int | None = None
            child_count: int | None = None
            children_json = "[]"

            for _field in range(reader.read_map_len()):
                field = reader.read_str()
                if field == "id":
                    node_id = reader.read_uint()
                elif field == "parentId":
                    parent_id = reader.read_uint_or_nil()
                elif field == "rule":
                    rule = reader.read_str()
                elif field == "text":
                    raw_text = reader.read_bin()
                    text = raw_text.decode("utf-8", errors="replace")
                    text_bytes = len(raw_text)
                elif field == "startLine":
                    start_line = reader.read_uint()
                elif field == "startColumn":
                    start_column = reader.read_uint()
                elif field == "endLine":
                    end_line = reader.read_uint()
                elif field == "endColumn":
                    end_column = reader.read_uint()
                elif field == "startByte":
                    start_byte = reader.read_uint()
                elif field == "endByte":
                    end_byte = reader.read_uint()
                elif field == "childCount":
                    child_count = reader.read_uint()
                elif field == "children":
                    children_json = read_child_summaries(reader)
                else:
                    reader.skip_value()

            yield AstNode(
                run_id=file_ast.run_id,
                parsed_file_id=file_ast.parsed_file_id,
                inventory_file_id=file_ast.inventory_file_id,
                project_name=file_ast.project_name,
                absolute_path=file_ast.absolute_path,
                file_name=file_ast.file_name,
                node_id=node_id,
                parent_id=parent_id,
                rule=rule,
                text=text,
                text_bytes=text_bytes,
                start_line=start_line,
                start_column=start_column,
                end_line=end_line,
                end_column=end_column,
                start_byte=start_byte,
                end_byte=end_byte,
                child_count=child_count,
                children_json=children_json,
            )

    if reader.pos != len(file_ast.ast_binary):
        raise ValueError(f"{file_ast.absolute_path}: MessagePack document has trailing bytes")


def save_nodes(conn: sqlite3.Connection, nodes: list[AstNode]) -> None:
    conn.executemany(
        """
        INSERT INTO ast_nodes(
            run_id,
            parsed_file_id,
            inventory_file_id,
            project_name,
            absolute_path,
            file_name,
            node_id,
            parent_id,
            rule,
            text,
            text_bytes,
            start_line,
            start_column,
            end_line,
            end_column,
            start_byte,
            end_byte,
            child_count,
            children_json
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                node.run_id,
                node.parsed_file_id,
                node.inventory_file_id,
                node.project_name,
                node.absolute_path,
                node.file_name,
                node.node_id,
                node.parent_id,
                node.rule,
                node.text,
                node.text_bytes,
                node.start_line,
                node.start_column,
                node.end_line,
                node.end_column,
                node.start_byte,
                node.end_byte,
                node.child_count,
                node.children_json,
            )
            for node in nodes
        ],
    )


def main() -> int:
    args = parse_args()
    db_path = args.db.resolve()
    if not db_path.is_file():
        print(f"ERROR: database does not exist: {db_path}")
        return 2

    conn = connect_db(db_path)
    started = time.perf_counter()
    try:
        create_schema(conn, recreate=args.recreate)
        drop_indexes(conn)
        file_count = count_files(conn, run_id=args.run_id, limit=args.limit)
        if not file_count:
            print("No parsed Java files found for the selected run.")
            return 2

        existing = conn.execute(
            "SELECT COUNT(*) FROM ast_nodes WHERE run_id = ?",
            (args.run_id,),
        ).fetchone()[0]
        if existing and not args.recreate:
            print(
                "ERROR: ast_nodes already has rows for this run. "
                "Use --recreate to rebuild the table."
            )
            return 2

        total_nodes = 0
        pending: list[AstNode] = []
        print(f"DB       : {db_path}")
        print(f"Run ID   : {args.run_id}")
        print(f"Files    : {file_count}")

        with conn:
            for index, file_ast in enumerate(
                iter_files(conn, run_id=args.run_id, limit=args.limit),
                start=1,
            ):
                for node in iter_nodes(file_ast):
                    total_nodes += 1
                    pending.append(node)

                    if len(pending) >= args.batch_size:
                        save_nodes(conn, pending)
                        pending.clear()

                if args.progress_every > 0 and index % args.progress_every == 0:
                    elapsed = time.perf_counter() - started
                    print(
                        f"Progress : {index}/{file_count} files "
                        f"nodes={total_nodes} elapsed={elapsed:.3f}s"
                    )

            if pending:
                save_nodes(conn, pending)

        create_indexes(conn)
        elapsed = time.perf_counter() - started
        print(f"Nodes    : {total_nodes}")
        print(f"Elapsed  : {elapsed:.3f}s")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
