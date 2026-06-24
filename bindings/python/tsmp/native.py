from __future__ import annotations

import ctypes
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TSMP_FORMAT_JSON = 1
TSMP_FORMAT_CSV = 2
TSMP_FORMAT_STATS = 3
TSMP_FORMAT_BINARY = 4
TSMP_FORMAT_DIAGNOSTICS = 5

TSMP_FIELD_ID = 1 << 0
TSMP_FIELD_PARENT_ID = 1 << 1
TSMP_FIELD_RULE = 1 << 2
TSMP_FIELD_TEXT = 1 << 3
TSMP_FIELD_RANGE = 1 << 4
TSMP_FIELD_BYTE_RANGE = 1 << 5
TSMP_FIELD_CHILD_COUNT = 1 << 6
TSMP_FIELD_CHILDREN = 1 << 7
TSMP_FIELD_DIAGNOSTICS = 1 << 8
TSMP_FIELD_ALL = 0xFFFFFFFF

FORMAT_NAMES = {
    "json": TSMP_FORMAT_JSON,
    "csv": TSMP_FORMAT_CSV,
    "stats": TSMP_FORMAT_STATS,
    "binary": TSMP_FORMAT_BINARY,
    "msgpack": TSMP_FORMAT_BINARY,
    "diagnostics": TSMP_FORMAT_DIAGNOSTICS,
}

FIELD_NAMES = {
    "id": TSMP_FIELD_ID,
    "parent_id": TSMP_FIELD_PARENT_ID,
    "parent": TSMP_FIELD_PARENT_ID,
    "rule": TSMP_FIELD_RULE,
    "text": TSMP_FIELD_TEXT,
    "range": TSMP_FIELD_RANGE,
    "byte_range": TSMP_FIELD_BYTE_RANGE,
    "bytes": TSMP_FIELD_BYTE_RANGE,
    "child_count": TSMP_FIELD_CHILD_COUNT,
    "children": TSMP_FIELD_CHILDREN,
    "diagnostics": TSMP_FIELD_DIAGNOSTICS,
    "all": TSMP_FIELD_ALL,
}


class TsmpError(RuntimeError):
    pass


class NativeParseError(TsmpError):
    pass


@dataclass(frozen=True)
class ParseResult:
    data: bytes
    node_count: int
    output_format: str

    @property
    def text(self) -> str:
        return self.data.decode("utf-8")

    def json(self) -> Any:
        return json.loads(self.data)


@dataclass(frozen=True)
class ParseSummary:
    output_length: int
    node_count: int
    output_format: str


@dataclass(frozen=True)
class LanguageLoadResult:
    language: str
    display_name: str


class _TsmpOptions(ctypes.Structure):
    _fields_ = [
        ("language", ctypes.c_char_p),
        ("format", ctypes.c_int),
        ("include_rules", ctypes.c_char_p),
        ("fields", ctypes.c_uint),
        ("include_tokens", ctypes.c_int),
        ("pretty", ctypes.c_int),
    ]


class _TsmpResult(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_int),
        ("data", ctypes.c_void_p),
        ("length", ctypes.c_size_t),
        ("node_count", ctypes.c_size_t),
        ("error_message", ctypes.c_void_p),
    ]


class _LanguageLoadResult(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_int),
        ("language", ctypes.c_void_p),
        ("display_name", ctypes.c_void_p),
        ("error_message", ctypes.c_void_p),
    ]


def default_library_path() -> Path:
    env_path = os.environ.get("FASTPARSE_LIBRARY_PATH") or os.environ.get("TSMP_LIBRARY_PATH")
    if env_path:
        return Path(env_path)

    project_root = Path(__file__).resolve().parents[3]
    if sys.platform == "darwin":
        candidates = ("libfastparse.dylib", "libtsmp.dylib", "libts_multi_parser.dylib")
    elif sys.platform == "win32":
        candidates = ("fastparse.dll", "tsmp.dll")
    else:
        candidates = ("libfastparse.so", "libtsmp.so", "libts_multi_parser.so")

    for directory in ("bin", "lib"):
        for name in candidates:
            candidate = project_root / directory / name
            if candidate.exists():
                return candidate
    return project_root / ("bin" if sys.platform == "win32" else "lib") / candidates[0]


def parse_field_mask(fields: int | str | Iterable[str] | None) -> int:
    if fields is None or fields == "":
        return 0
    if isinstance(fields, int):
        return fields
    if isinstance(fields, str):
        raw_names = fields.split(",")
    else:
        raw_names = fields

    mask = 0
    for name in raw_names:
        normalized = str(name).strip().lower().replace("-", "_")
        if not normalized:
            continue
        try:
            value = FIELD_NAMES[normalized]
        except KeyError as exc:
            valid = ", ".join(sorted(FIELD_NAMES))
            raise ValueError(f"unknown field '{name}'. Valid fields: {valid}") from exc
        if value == TSMP_FIELD_ALL:
            return 0
        mask |= value
    return mask


def _format_value(output_format: str | int) -> tuple[str, int]:
    if isinstance(output_format, int):
        for name, value in FORMAT_NAMES.items():
            if value == output_format:
                return name, value
        raise ValueError(f"unknown TSMP format value: {output_format}")

    normalized = output_format.strip().lower().replace("-", "_")
    try:
        return normalized, FORMAT_NAMES[normalized]
    except KeyError as exc:
        valid = ", ".join(sorted(FORMAT_NAMES))
        raise ValueError(f"unknown format '{output_format}'. Valid formats: {valid}") from exc


def _rules_value(include_rules: str | Iterable[str] | None) -> bytes | None:
    if include_rules is None:
        return None
    if isinstance(include_rules, str):
        value = include_rules
    else:
        value = "|".join(rule for rule in include_rules if rule)
    return value.encode("utf-8") if value else None


def _native_string(pointer: Any) -> str:
    if not pointer:
        return ""
    return ctypes.string_at(pointer).decode("utf-8", errors="replace")


def _native_function(lib: ctypes.CDLL, preferred: str, fallback: str) -> Any:
    try:
        return getattr(lib, preferred)
    except AttributeError:
        return getattr(lib, fallback)


class Tsmp:
    def __init__(self, library_path: str | Path | None = None) -> None:
        self.library_path = Path(library_path) if library_path else default_library_path()
        self._dll_directory = None
        if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
            self._dll_directory = os.add_dll_directory(str(self.library_path.parent))
        self._lib = ctypes.CDLL(str(self.library_path))

        self._version_fn = _native_function(self._lib, "fastparse_version", "tsmp_version")
        self._parse_fn = _native_function(self._lib, "fastparse_parse", "tsmp_parse")
        self._free_fn = _native_function(self._lib, "fastparse_result_free", "tsmp_result_free")
        self._load_language_extension_fn = getattr(self._lib, "fastparse_load_language_extension")
        self._language_available_fn = getattr(self._lib, "fastparse_language_available")
        self._language_load_result_free_fn = getattr(self._lib, "fastparse_language_load_result_free")

        self._version_fn.argtypes = []
        self._version_fn.restype = ctypes.c_char_p

        self._parse_fn.argtypes = [
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(_TsmpOptions),
            ctypes.POINTER(_TsmpResult),
        ]
        self._parse_fn.restype = ctypes.c_int

        self._free_fn.argtypes = [ctypes.POINTER(_TsmpResult)]
        self._free_fn.restype = None

        self._load_language_extension_fn.argtypes = [ctypes.c_char_p, ctypes.POINTER(_LanguageLoadResult)]
        self._load_language_extension_fn.restype = ctypes.c_int

        self._language_available_fn.argtypes = [ctypes.c_char_p]
        self._language_available_fn.restype = ctypes.c_int

        self._language_load_result_free_fn.argtypes = [ctypes.POINTER(_LanguageLoadResult)]
        self._language_load_result_free_fn.restype = None

    @property
    def version(self) -> str:
        return self._version_fn().decode("utf-8")

    def language_available(self, language: str) -> bool:
        return bool(self._language_available_fn(language.encode("utf-8")))

    def load_language_extension(self, path: str | Path) -> LanguageLoadResult:
        result = _LanguageLoadResult()
        status = self._load_language_extension_fn(str(path).encode("utf-8"), ctypes.byref(result))
        try:
            if status != 0 or result.status != 0:
                message = _native_string(result.error_message)
                raise NativeParseError(
                    f"fastparse_load_language_extension failed with status {status}/{result.status}: "
                    f"{message or 'no error detail'}"
                )
            return LanguageLoadResult(
                language=_native_string(result.language),
                display_name=_native_string(result.display_name),
            )
        finally:
            self._language_load_result_free_fn(ctypes.byref(result))

    def parse_bytes(
        self,
        source: bytes | bytearray | memoryview,
        *,
        language: str = "java",
        output_format: str | int = "json",
        include_rules: str | Iterable[str] | None = None,
        fields: int | str | Iterable[str] | None = None,
        include_tokens: bool = False,
        pretty: bool = False,
    ) -> ParseResult:
        data, node_count, format_name, _output_length = self._parse_native(
            source,
            language=language,
            output_format=output_format,
            include_rules=include_rules,
            fields=fields,
            include_tokens=include_tokens,
            pretty=pretty,
            copy_data=True,
        )
        return ParseResult(data, node_count, format_name)

    def parse_bytes_summary(
        self,
        source: bytes | bytearray | memoryview,
        *,
        language: str = "java",
        output_format: str | int = "json",
        include_rules: str | Iterable[str] | None = None,
        fields: int | str | Iterable[str] | None = None,
        include_tokens: bool = False,
        pretty: bool = False,
    ) -> ParseSummary:
        _data, node_count, format_name, output_length = self._parse_native(
            source,
            language=language,
            output_format=output_format,
            include_rules=include_rules,
            fields=fields,
            include_tokens=include_tokens,
            pretty=pretty,
            copy_data=False,
        )
        return ParseSummary(output_length, node_count, format_name)

    def _parse_native(
        self,
        source: bytes | bytearray | memoryview,
        *,
        language: str,
        output_format: str | int,
        include_rules: str | Iterable[str] | None,
        fields: int | str | Iterable[str] | None,
        include_tokens: bool,
        pretty: bool,
        copy_data: bool,
    ) -> tuple[bytes, int, str, int]:
        source_bytes = source if isinstance(source, bytes) else bytes(source)
        format_name, format_code = _format_value(output_format)
        source_pointer = ctypes.c_char_p(source_bytes) if source_bytes else None
        options = _TsmpOptions(
            language.encode("utf-8"),
            format_code,
            _rules_value(include_rules),
            parse_field_mask(fields),
            1 if include_tokens else 0,
            1 if pretty else 0,
        )
        result = _TsmpResult()

        status = self._parse_fn(
            ctypes.cast(source_pointer, ctypes.c_void_p) if source_pointer is not None else None,
            len(source_bytes),
            ctypes.byref(options),
            ctypes.byref(result),
        )

        try:
            if status != 0 or result.status != 0:
                message = _native_string(result.error_message)
                raise NativeParseError(
                    f"tsmp_parse failed with status {status}/{result.status}: "
                    f"{message or 'no error detail'}"
                )
            output_length = int(result.length)
            data = (
                ctypes.string_at(result.data, result.length)
                if copy_data and result.data and result.length > 0
                else b""
            )
            return data, int(result.node_count), format_name, output_length
        finally:
            self._free_fn(ctypes.byref(result))

    def parse_text(
        self,
        source: str,
        *,
        encoding: str = "utf-8",
        errors: str = "strict",
        **kwargs: Any,
    ) -> ParseResult:
        return self.parse_bytes(source.encode(encoding, errors=errors), **kwargs)

    def parse_result(self, source: bytes | bytearray | memoryview, **kwargs: Any) -> tuple[bytes, int]:
        result = self.parse_bytes(source, **kwargs)
        return result.data, result.node_count

    def parse(self, source: bytes | bytearray | memoryview, **kwargs: Any) -> bytes:
        return self.parse_bytes(source, **kwargs).data


TsmpLibrary = Tsmp
FastParse = Tsmp
