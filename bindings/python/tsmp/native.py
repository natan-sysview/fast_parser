from __future__ import annotations

import ctypes
import importlib
import importlib.resources
import json
import os
import platform
import sys
from dataclasses import dataclass
from enum import IntEnum, IntFlag
from pathlib import Path
from typing import Any, Iterable

from .binary import BinaryDocument, decode_binary


TSMP_FORMAT_JSON = 1
TSMP_FORMAT_CSV = 2
TSMP_FORMAT_STATS = 3
TSMP_FORMAT_BINARY = 4
TSMP_FORMAT_DIAGNOSTICS = 5

TSMP_NORMALIZATION_AUTO_SAFE = 0
TSMP_NORMALIZATION_NONE = 1
TSMP_NORMALIZATION_COBOL_FIXED_LEGACY = 2

TSMP_FIELD_ID = 1 << 0
TSMP_FIELD_PARENT_ID = 1 << 1
TSMP_FIELD_RULE = 1 << 2
TSMP_FIELD_TEXT = 1 << 3
TSMP_FIELD_RANGE = 1 << 4
TSMP_FIELD_BYTE_RANGE = 1 << 5
TSMP_FIELD_CHILD_COUNT = 1 << 6
TSMP_FIELD_CHILDREN = 1 << 7
TSMP_FIELD_DIAGNOSTICS = 1 << 8
TSMP_FIELD_CAPTURE_NAME = 1 << 9
TSMP_FIELD_PATTERN_INDEX = 1 << 10
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
    "capture_name": TSMP_FIELD_CAPTURE_NAME,
    "capture": TSMP_FIELD_CAPTURE_NAME,
    "name": TSMP_FIELD_CAPTURE_NAME,
    "pattern_index": TSMP_FIELD_PATTERN_INDEX,
    "pattern": TSMP_FIELD_PATTERN_INDEX,
    "all": TSMP_FIELD_ALL,
}

NORMALIZATION_NAMES = {
    "auto": TSMP_NORMALIZATION_AUTO_SAFE,
    "auto_safe": TSMP_NORMALIZATION_AUTO_SAFE,
    "safe": TSMP_NORMALIZATION_AUTO_SAFE,
    "none": TSMP_NORMALIZATION_NONE,
    "off": TSMP_NORMALIZATION_NONE,
    "cobol_fixed_legacy": TSMP_NORMALIZATION_COBOL_FIXED_LEGACY,
    "cobol": TSMP_NORMALIZATION_COBOL_FIXED_LEGACY,
}


class OutputFormat(IntEnum):
    JSON = TSMP_FORMAT_JSON
    CSV = TSMP_FORMAT_CSV
    STATS = TSMP_FORMAT_STATS
    BINARY = TSMP_FORMAT_BINARY
    DIAGNOSTICS = TSMP_FORMAT_DIAGNOSTICS


class Field(IntFlag):
    ID = TSMP_FIELD_ID
    PARENT_ID = TSMP_FIELD_PARENT_ID
    RULE = TSMP_FIELD_RULE
    TEXT = TSMP_FIELD_TEXT
    RANGE = TSMP_FIELD_RANGE
    BYTE_RANGE = TSMP_FIELD_BYTE_RANGE
    CHILD_COUNT = TSMP_FIELD_CHILD_COUNT
    CHILDREN = TSMP_FIELD_CHILDREN
    DIAGNOSTICS = TSMP_FIELD_DIAGNOSTICS
    CAPTURE_NAME = TSMP_FIELD_CAPTURE_NAME
    PATTERN_INDEX = TSMP_FIELD_PATTERN_INDEX
    ALL = TSMP_FIELD_ALL


class Normalization(IntEnum):
    AUTO_SAFE = TSMP_NORMALIZATION_AUTO_SAFE
    NONE = TSMP_NORMALIZATION_NONE
    COBOL_FIXED_LEGACY = TSMP_NORMALIZATION_COBOL_FIXED_LEGACY


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

    def binary_document(self) -> BinaryDocument:
        return decode_binary(self.data)


@dataclass(frozen=True)
class ParseSummary:
    output_length: int
    node_count: int
    output_format: str


@dataclass(frozen=True)
class LanguageLoadResult:
    language: str
    display_name: str


@dataclass(frozen=True)
class ParseOptions:
    language: str = "java"
    output_format: str | int | OutputFormat = OutputFormat.JSON
    include_rules: str | Iterable[str] | None = None
    fields: int | str | Iterable[str] | Field | None = None
    include_tokens: bool = False
    pretty: bool = False
    normalization: str | int | Normalization | None = None


@dataclass(frozen=True)
class QueryOptions:
    language: str = "java"
    output_format: str | int | OutputFormat = OutputFormat.JSON
    fields: int | str | Iterable[str] | Field | None = None
    max_matches: int = 0
    max_captures: int = 0
    include_pattern: bool = True
    pretty: bool = False
    normalization: str | int | Normalization | None = None


class _TsmpOptions(ctypes.Structure):
    _fields_ = [
        ("language", ctypes.c_char_p),
        ("format", ctypes.c_int),
        ("include_rules", ctypes.c_char_p),
        ("fields", ctypes.c_uint),
        ("include_tokens", ctypes.c_int),
        ("pretty", ctypes.c_int),
    ]


class _TsmpOptionsV2(ctypes.Structure):
    _fields_ = [
        ("language", ctypes.c_char_p),
        ("format", ctypes.c_int),
        ("include_rules", ctypes.c_char_p),
        ("fields", ctypes.c_uint),
        ("include_tokens", ctypes.c_int),
        ("pretty", ctypes.c_int),
        ("normalization", ctypes.c_int),
    ]


class _TsmpQueryOptions(ctypes.Structure):
    _fields_ = [
        ("language", ctypes.c_char_p),
        ("format", ctypes.c_int),
        ("fields", ctypes.c_uint),
        ("max_matches", ctypes.c_size_t),
        ("max_captures", ctypes.c_size_t),
        ("include_pattern", ctypes.c_int),
        ("pretty", ctypes.c_int),
        ("normalization", ctypes.c_int),
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

    site_packages = Path(__file__).resolve().parents[1]
    wheel_native_dirs = (
        Path(__file__).resolve().parent / "native",
        site_packages / "fastparse" / "native",
    )
    for directory in wheel_native_dirs:
        for name in candidates:
            candidate = directory / name
            if candidate.exists():
                return candidate

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
        value = int(fields)
        return 0 if value == TSMP_FIELD_ALL else value
    if isinstance(fields, str):
        raw_names = fields.split(",")
    else:
        raw_names = fields

    mask = 0
    for name in raw_names:
        if isinstance(name, int):
            value = int(name)
            if value == TSMP_FIELD_ALL:
                return 0
            mask |= value
            continue
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


def _normalization_value(normalization: str | int | None) -> tuple[str, int]:
    if normalization is None:
        return "auto_safe", TSMP_NORMALIZATION_AUTO_SAFE
    if isinstance(normalization, int):
        for name, value in NORMALIZATION_NAMES.items():
            if value == normalization:
                return name, value
        raise ValueError(f"unknown TSMP normalization value: {normalization}")

    normalized = normalization.strip().lower().replace("-", "_")
    try:
        return normalized, NORMALIZATION_NAMES[normalized]
    except KeyError as exc:
        valid = ", ".join(sorted(NORMALIZATION_NAMES))
        raise ValueError(f"unknown normalization '{normalization}'. Valid values: {valid}") from exc


def _rules_value(include_rules: str | Iterable[str] | None) -> bytes | None:
    if include_rules is None:
        return None
    if isinstance(include_rules, str):
        value = include_rules
    else:
        value = "|".join(rule for rule in include_rules if rule)
    return value.encode("utf-8") if value else None


_UNSET = object()


def _merge_options(
    options: ParseOptions | None,
    *,
    language: Any,
    output_format: Any,
    include_rules: Any,
    fields: Any,
    include_tokens: Any,
    pretty: Any,
    normalization: Any,
) -> ParseOptions:
    base = options or ParseOptions()
    return ParseOptions(
        language=base.language if language is _UNSET else language,
        output_format=base.output_format if output_format is _UNSET else output_format,
        include_rules=base.include_rules if include_rules is _UNSET else include_rules,
        fields=base.fields if fields is _UNSET else fields,
        include_tokens=base.include_tokens if include_tokens is _UNSET else bool(include_tokens),
        pretty=base.pretty if pretty is _UNSET else bool(pretty),
        normalization=base.normalization if normalization is _UNSET else normalization,
    )


def _merge_query_options(
    options: QueryOptions | None,
    *,
    language: Any,
    output_format: Any,
    fields: Any,
    max_matches: Any,
    max_captures: Any,
    include_pattern: Any,
    pretty: Any,
    normalization: Any,
) -> QueryOptions:
    base = options or QueryOptions()
    return QueryOptions(
        language=base.language if language is _UNSET else language,
        output_format=base.output_format if output_format is _UNSET else output_format,
        fields=base.fields if fields is _UNSET else fields,
        max_matches=base.max_matches if max_matches is _UNSET else int(max_matches),
        max_captures=base.max_captures if max_captures is _UNSET else int(max_captures),
        include_pattern=base.include_pattern if include_pattern is _UNSET else bool(include_pattern),
        pretty=base.pretty if pretty is _UNSET else bool(pretty),
        normalization=base.normalization if normalization is _UNSET else normalization,
    )


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
        self._parse_v2_fn = getattr(self._lib, "fastparse_parse_v2", None)
        self._query_fn = _native_function(self._lib, "fastparse_query", "tsmp_query")
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

        if self._parse_v2_fn is not None:
            self._parse_v2_fn.argtypes = [
                ctypes.c_void_p,
                ctypes.c_size_t,
                ctypes.POINTER(_TsmpOptionsV2),
                ctypes.POINTER(_TsmpResult),
            ]
            self._parse_v2_fn.restype = ctypes.c_int

        self._query_fn.argtypes = [
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(_TsmpQueryOptions),
            ctypes.POINTER(_TsmpResult),
        ]
        self._query_fn.restype = ctypes.c_int

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

    def load_bundled_language(self, language: str) -> LanguageLoadResult:
        """Load an installed FastParse language package such as fastparse-language-python."""
        if self.language_available(language):
            return LanguageLoadResult(language=language, display_name=language)
        extension_path = bundled_language_extension_path(language)
        load_result = self.load_language_extension(extension_path)
        if not self.language_available(language):
            raise NativeParseError(
                f"bundled FastParse language package loaded {load_result.language!r}, "
                f"but {language!r} is still unavailable"
            )
        return load_result

    def parse_bytes(
        self,
        source: bytes | bytearray | memoryview,
        options: ParseOptions | None = None,
        *,
        language: str | object = _UNSET,
        output_format: str | int | OutputFormat | object = _UNSET,
        include_rules: str | Iterable[str] | object | None = _UNSET,
        fields: int | str | Iterable[str] | Field | object | None = _UNSET,
        include_tokens: bool | object = _UNSET,
        pretty: bool | object = _UNSET,
        normalization: str | int | Normalization | object | None = _UNSET,
    ) -> ParseResult:
        merged = _merge_options(
            options,
            language=language,
            output_format=output_format,
            include_rules=include_rules,
            fields=fields,
            include_tokens=include_tokens,
            pretty=pretty,
            normalization=normalization,
        )
        data, node_count, format_name, _output_length = self._parse_native(
            source,
            language=merged.language,
            output_format=merged.output_format,
            include_rules=merged.include_rules,
            fields=merged.fields,
            include_tokens=merged.include_tokens,
            pretty=merged.pretty,
            normalization=merged.normalization,
            copy_data=True,
        )
        return ParseResult(data, node_count, format_name)

    def parse_bytes_summary(
        self,
        source: bytes | bytearray | memoryview,
        options: ParseOptions | None = None,
        *,
        language: str | object = _UNSET,
        output_format: str | int | OutputFormat | object = _UNSET,
        include_rules: str | Iterable[str] | object | None = _UNSET,
        fields: int | str | Iterable[str] | Field | object | None = _UNSET,
        include_tokens: bool | object = _UNSET,
        pretty: bool | object = _UNSET,
        normalization: str | int | Normalization | object | None = _UNSET,
    ) -> ParseSummary:
        merged = _merge_options(
            options,
            language=language,
            output_format=output_format,
            include_rules=include_rules,
            fields=fields,
            include_tokens=include_tokens,
            pretty=pretty,
            normalization=normalization,
        )
        _data, node_count, format_name, output_length = self._parse_native(
            source,
            language=merged.language,
            output_format=merged.output_format,
            include_rules=merged.include_rules,
            fields=merged.fields,
            include_tokens=merged.include_tokens,
            pretty=merged.pretty,
            normalization=merged.normalization,
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
        normalization: str | int | None,
        copy_data: bool,
    ) -> tuple[bytes, int, str, int]:
        source_bytes = source if isinstance(source, bytes) else bytes(source)
        format_name, format_code = _format_value(output_format)
        _normalization_name, normalization_code = _normalization_value(normalization)
        source_pointer = ctypes.c_char_p(source_bytes) if source_bytes else None
        if self._parse_v2_fn is not None:
            options = _TsmpOptionsV2(
                language.encode("utf-8"),
                format_code,
                _rules_value(include_rules),
                parse_field_mask(fields),
                1 if include_tokens else 0,
                1 if pretty else 0,
                normalization_code,
            )
            parse_fn = self._parse_v2_fn
        else:
            if normalization_code != TSMP_NORMALIZATION_AUTO_SAFE:
                raise TsmpError("native FastParse library does not support explicit normalization options")
            options = _TsmpOptions(
                language.encode("utf-8"),
                format_code,
                _rules_value(include_rules),
                parse_field_mask(fields),
                1 if include_tokens else 0,
                1 if pretty else 0,
            )
            parse_fn = self._parse_fn
        result = _TsmpResult()

        status = parse_fn(
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
        options: ParseOptions | None = None,
        *,
        encoding: str = "utf-8",
        errors: str = "strict",
        **kwargs: Any,
    ) -> ParseResult:
        return self.parse_bytes(source.encode(encoding, errors=errors), options, **kwargs)

    def parse_text_summary(
        self,
        source: str,
        options: ParseOptions | None = None,
        *,
        encoding: str = "utf-8",
        errors: str = "strict",
        **kwargs: Any,
    ) -> ParseSummary:
        return self.parse_bytes_summary(source.encode(encoding, errors=errors), options, **kwargs)

    def query_bytes(
        self,
        source: bytes | bytearray | memoryview,
        query: str | bytes | bytearray | memoryview,
        options: QueryOptions | None = None,
        *,
        language: str | object = _UNSET,
        output_format: str | int | OutputFormat | object = _UNSET,
        fields: int | str | Iterable[str] | Field | object | None = _UNSET,
        max_matches: int | object = _UNSET,
        max_captures: int | object = _UNSET,
        include_pattern: bool | object = _UNSET,
        pretty: bool | object = _UNSET,
        normalization: str | int | Normalization | object | None = _UNSET,
    ) -> ParseResult:
        merged = _merge_query_options(
            options,
            language=language,
            output_format=output_format,
            fields=fields,
            max_matches=max_matches,
            max_captures=max_captures,
            include_pattern=include_pattern,
            pretty=pretty,
            normalization=normalization,
        )
        data, capture_count, format_name, _output_length = self._query_native(
            source,
            query,
            language=merged.language,
            output_format=merged.output_format,
            fields=merged.fields,
            max_matches=merged.max_matches,
            max_captures=merged.max_captures,
            include_pattern=merged.include_pattern,
            pretty=merged.pretty,
            normalization=merged.normalization,
            copy_data=True,
        )
        return ParseResult(data, capture_count, format_name)

    def query_bytes_summary(
        self,
        source: bytes | bytearray | memoryview,
        query: str | bytes | bytearray | memoryview,
        options: QueryOptions | None = None,
        **kwargs: Any,
    ) -> ParseSummary:
        merged = _merge_query_options(
            options,
            language=kwargs.pop("language", _UNSET),
            output_format=kwargs.pop("output_format", _UNSET),
            fields=kwargs.pop("fields", _UNSET),
            max_matches=kwargs.pop("max_matches", _UNSET),
            max_captures=kwargs.pop("max_captures", _UNSET),
            include_pattern=kwargs.pop("include_pattern", _UNSET),
            pretty=kwargs.pop("pretty", _UNSET),
            normalization=kwargs.pop("normalization", _UNSET),
        )
        if kwargs:
            unknown = ", ".join(sorted(kwargs))
            raise TypeError(f"unexpected keyword argument(s): {unknown}")
        _data, capture_count, format_name, output_length = self._query_native(
            source,
            query,
            language=merged.language,
            output_format=merged.output_format,
            fields=merged.fields,
            max_matches=merged.max_matches,
            max_captures=merged.max_captures,
            include_pattern=merged.include_pattern,
            pretty=merged.pretty,
            normalization=merged.normalization,
            copy_data=False,
        )
        return ParseSummary(output_length, capture_count, format_name)

    def query_text(
        self,
        source: str,
        query: str,
        options: QueryOptions | None = None,
        *,
        encoding: str = "utf-8",
        errors: str = "strict",
        **kwargs: Any,
    ) -> ParseResult:
        return self.query_bytes(source.encode(encoding, errors=errors), query, options, **kwargs)

    def query_text_summary(
        self,
        source: str,
        query: str,
        options: QueryOptions | None = None,
        *,
        encoding: str = "utf-8",
        errors: str = "strict",
        **kwargs: Any,
    ) -> ParseSummary:
        return self.query_bytes_summary(source.encode(encoding, errors=errors), query, options, **kwargs)

    def _query_native(
        self,
        source: bytes | bytearray | memoryview,
        query: str | bytes | bytearray | memoryview,
        *,
        language: str,
        output_format: str | int,
        fields: int | str | Iterable[str] | None,
        max_matches: int,
        max_captures: int,
        include_pattern: bool,
        pretty: bool,
        normalization: str | int | None,
        copy_data: bool,
    ) -> tuple[bytes, int, str, int]:
        source_bytes = source if isinstance(source, bytes) else bytes(source)
        query_bytes = query.encode("utf-8") if isinstance(query, str) else bytes(query)
        format_name, format_code = _format_value(output_format)
        _normalization_name, normalization_code = _normalization_value(normalization)
        source_pointer = ctypes.c_char_p(source_bytes) if source_bytes else None
        query_pointer = ctypes.c_char_p(query_bytes) if query_bytes else None
        options = _TsmpQueryOptions(
            language.encode("utf-8"),
            format_code,
            parse_field_mask(fields),
            max(0, int(max_matches)),
            max(0, int(max_captures)),
            1 if include_pattern else 0,
            1 if pretty else 0,
            normalization_code,
        )
        result = _TsmpResult()
        status = self._query_fn(
            ctypes.cast(source_pointer, ctypes.c_void_p) if source_pointer is not None else None,
            len(source_bytes),
            ctypes.cast(query_pointer, ctypes.c_void_p) if query_pointer is not None else None,
            len(query_bytes),
            ctypes.byref(options),
            ctypes.byref(result),
        )

        try:
            if status != 0 or result.status != 0:
                message = _native_string(result.error_message)
                raise NativeParseError(
                    f"tsmp_query failed with status {status}/{result.status}: "
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

    def parse_result(self, source: bytes | bytearray | memoryview, **kwargs: Any) -> tuple[bytes, int]:
        result = self.parse_bytes(source, **kwargs)
        return result.data, result.node_count

    def parse(self, source: bytes | bytearray | memoryview, **kwargs: Any) -> bytes:
        return self.parse_bytes(source, **kwargs).data


TsmpLibrary = Tsmp
FastParse = Tsmp


def bundled_language_extension_path(language: str) -> Path:
    canonical = language.strip().lower().replace("-", "_")
    if not canonical:
        raise ValueError("language is required")

    env_name = f"FASTPARSE_LANGUAGE_{canonical.upper()}_PATH"
    if os.environ.get(env_name):
        return Path(os.environ[env_name])

    package_name = f"fastparse_language_{canonical}"
    try:
        package = importlib.import_module(package_name)
    except ModuleNotFoundError as exc:
        raise FileNotFoundError(
            f"FastParse language package '{package_name}' is not installed. "
            f"Install it with: pip install fastparse-language-{language}"
        ) from exc

    extension_path_fn = getattr(package, "extension_path", None)
    if callable(extension_path_fn):
        return Path(extension_path_fn())

    file_name = _language_extension_file_name(canonical)
    platform_key = _language_platform_key()
    package_root = importlib.resources.files(package)
    candidates = [
        package_root / "native" / platform_key / file_name,
        package_root / "native" / file_name,
    ]
    for candidate in candidates:
        candidate_path = Path(str(candidate))
        if candidate_path.is_file():
            return candidate_path

    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(
        f"FastParse language package '{package_name}' does not include a native asset "
        f"for {platform_key}. Searched: {searched}"
    )


def _language_extension_file_name(language: str) -> str:
    if sys.platform == "darwin":
        return f"libfastparse_language_{language}.dylib"
    if sys.platform == "win32":
        return f"fastparse_language_{language}.dll"
    return f"libfastparse_language_{language}.so"


def _language_platform_key() -> str:
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        arch = "x64"
    elif machine in {"arm64", "aarch64"}:
        arch = "arm64"
    else:
        arch = machine

    if sys.platform == "darwin":
        return f"osx-{arch}"
    if sys.platform == "win32":
        return f"win-{arch}"
    return f"linux-{arch}"
