#!/usr/bin/env python3
"""Create a SQLite inventory of Java files under a project collection."""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = Path("/Users/natanbarronlugo/Desktop/Proyectos/javaswing/componentes")
DEFAULT_DB = ROOT / "data" / "java_swing_inventory.sqlite"

PACKAGE_RE = re.compile(rb"(?m)^\s*package\s+([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\s*;")


@dataclass(frozen=True)
class JavaFile:
    project_name: str
    project_root: Path
    absolute_path: Path
    root_relative_path: str
    project_relative_path: str
    file_name: str
    package_name: str
    size_bytes: int
    line_count: int
    mtime_epoch: float
    sha256: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a SQLite inventory of Java files.")
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--no-hash", action="store_true", help="Skip SHA-256 calculation.")
    return parser.parse_args()


def project_for_file(source_root: Path, java_file: Path) -> tuple[str, Path]:
    relative = java_file.relative_to(source_root)
    first = relative.parts[0] if relative.parts else source_root.name
    return first, source_root / first


def package_from_bytes(data: bytes) -> str:
    match = PACKAGE_RE.search(data[:65536])
    if not match:
        return ""
    return match.group(1).decode("ascii", errors="ignore")


def sha256_hex(data: bytes, enabled: bool) -> str:
    if not enabled:
        return ""
    return hashlib.sha256(data).hexdigest()


def count_lines(data: bytes) -> int:
    if not data:
        return 0
    return data.count(b"\n") + (0 if data.endswith(b"\n") else 1)


def discover_java_files(source_root: Path, *, hash_files: bool) -> list[JavaFile]:
    files: list[JavaFile] = []
    for java_path in sorted(path for path in source_root.rglob("*.java") if path.is_file()):
        data = java_path.read_bytes()
        stat = java_path.stat()
        project_name, project_root = project_for_file(source_root, java_path)
        files.append(
            JavaFile(
                project_name=project_name,
                project_root=project_root,
                absolute_path=java_path,
                root_relative_path=java_path.relative_to(source_root).as_posix(),
                project_relative_path=java_path.relative_to(project_root).as_posix(),
                file_name=java_path.name,
                package_name=package_from_bytes(data),
                size_bytes=stat.st_size,
                line_count=count_lines(data),
                mtime_epoch=stat.st_mtime,
                sha256=sha256_hex(data, hash_files),
            )
        )
    return files


def connect_database(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def recreate_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP VIEW IF EXISTS v_project_summary;
        DROP TABLE IF EXISTS java_files;
        DROP TABLE IF EXISTS projects;
        DROP TABLE IF EXISTS metadata;

        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            root_path TEXT NOT NULL,
            relative_path TEXT NOT NULL,
            java_count INTEGER NOT NULL DEFAULT 0,
            total_bytes INTEGER NOT NULL DEFAULT 0,
            total_lines INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE java_files (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            project_name TEXT NOT NULL,
            absolute_path TEXT NOT NULL UNIQUE,
            root_relative_path TEXT NOT NULL,
            project_relative_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            package_name TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            line_count INTEGER NOT NULL,
            mtime_epoch REAL NOT NULL,
            sha256 TEXT NOT NULL
        );

        CREATE INDEX idx_java_files_project_id ON java_files(project_id);
        CREATE INDEX idx_java_files_project_name ON java_files(project_name);
        CREATE INDEX idx_java_files_package_name ON java_files(package_name);
        CREATE INDEX idx_java_files_file_name ON java_files(file_name);
        CREATE INDEX idx_java_files_root_relative_path ON java_files(root_relative_path);

        CREATE VIEW v_project_summary AS
        SELECT
            p.id,
            p.name,
            p.root_path,
            p.relative_path,
            p.java_count,
            p.total_bytes,
            p.total_lines
        FROM projects p
        ORDER BY p.java_count DESC, p.name ASC;
        """
    )


def write_inventory(conn: sqlite3.Connection, source_root: Path, files: list[JavaFile]) -> None:
    generated_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    projects = sorted({item.project_name: item.project_root for item in files}.items())

    with conn:
        recreate_schema(conn)
        conn.executemany(
            "INSERT INTO metadata(key, value) VALUES(?, ?)",
            [
                ("source_root", str(source_root)),
                ("generated_at", generated_at),
                ("java_file_count", str(len(files))),
                ("project_count", str(len(projects))),
                ("schema_version", "1"),
            ],
        )

        for project_name, project_root in projects:
            conn.execute(
                """
                INSERT INTO projects(name, root_path, relative_path)
                VALUES(?, ?, ?)
                """,
                (project_name, str(project_root), project_root.relative_to(source_root).as_posix()),
            )

        project_ids = {
            name: project_id
            for project_id, name in conn.execute("SELECT id, name FROM projects")
        }

        conn.executemany(
            """
            INSERT INTO java_files(
                project_id,
                project_name,
                absolute_path,
                root_relative_path,
                project_relative_path,
                file_name,
                package_name,
                size_bytes,
                line_count,
                mtime_epoch,
                sha256
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    project_ids[item.project_name],
                    item.project_name,
                    str(item.absolute_path),
                    item.root_relative_path,
                    item.project_relative_path,
                    item.file_name,
                    item.package_name,
                    item.size_bytes,
                    item.line_count,
                    item.mtime_epoch,
                    item.sha256,
                )
                for item in files
            ],
        )

        conn.execute(
            """
            UPDATE projects
            SET
                java_count = (
                    SELECT COUNT(*)
                    FROM java_files
                    WHERE java_files.project_id = projects.id
                ),
                total_bytes = (
                    SELECT COALESCE(SUM(size_bytes), 0)
                    FROM java_files
                    WHERE java_files.project_id = projects.id
                ),
                total_lines = (
                    SELECT COALESCE(SUM(line_count), 0)
                    FROM java_files
                    WHERE java_files.project_id = projects.id
                )
            """
        )


def print_summary(conn: sqlite3.Connection, db_path: Path) -> None:
    java_count = conn.execute("SELECT COUNT(*) FROM java_files").fetchone()[0]
    project_count = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    total_bytes = conn.execute("SELECT COALESCE(SUM(size_bytes), 0) FROM java_files").fetchone()[0]
    total_lines = conn.execute("SELECT COALESCE(SUM(line_count), 0) FROM java_files").fetchone()[0]

    print(f"DB           : {db_path}")
    print(f"Projects     : {project_count}")
    print(f"Java files   : {java_count}")
    print(f"Source bytes : {total_bytes}")
    print(f"Source lines : {total_lines}")
    print("Top projects :")
    for name, count, bytes_, lines in conn.execute(
        """
        SELECT name, java_count, total_bytes, total_lines
        FROM v_project_summary
        LIMIT 10
        """
    ):
        print(f"  {name:<58} {count:>5} files {lines:>9} lines {bytes_:>10} bytes")


def main() -> int:
    args = parse_args()
    source_root = args.source_root.resolve()
    db_path = args.db.resolve()

    if not source_root.is_dir():
        print(f"ERROR: source root does not exist: {source_root}")
        return 2

    files = discover_java_files(source_root, hash_files=not args.no_hash)
    conn = connect_database(db_path)
    try:
        write_inventory(conn, source_root, files)
        print_summary(conn, db_path)
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
