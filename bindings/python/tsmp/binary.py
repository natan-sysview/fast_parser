from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class MessagePackDecodeError(ValueError):
    pass


@dataclass(frozen=True)
class BinaryChild:
    rule: str | None = None
    text: bytes | None = None


@dataclass(frozen=True)
class BinaryNode:
    id: int | None = None
    parent_id: int | None = None
    rule: str | None = None
    text: bytes | None = None
    start_line: int | None = None
    start_column: int | None = None
    end_line: int | None = None
    end_column: int | None = None
    start_byte: int | None = None
    end_byte: int | None = None
    child_count: int | None = None
    is_error: bool | None = None
    is_missing: bool | None = None
    has_error: bool | None = None
    children: list[BinaryChild] = field(default_factory=list)


@dataclass(frozen=True)
class BinaryDocument:
    format: str
    schema_version: int
    language: str
    nodes: list[BinaryNode]
    node_count: int
    has_errors: bool | None = None
    error_node_count: int | None = None
    missing_node_count: int | None = None
    error_byte_count: int | None = None


class _Reader:
    def __init__(self, data: bytes | bytearray | memoryview) -> None:
        self.data = bytes(data)
        self.index = 0

    @property
    def end(self) -> bool:
        return self.index == len(self.data)

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
        if 0xE0 <= code <= 0xFF:
            return code - 0x100
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
        if code == 0xD0:
            return self._i8()
        if code == 0xD1:
            return self._i16()
        if code == 0xD2:
            return self._i32()
        if code == 0xD3:
            return self._i64()
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
        raise MessagePackDecodeError(f"unsupported MessagePack code: 0x{code:02x}")

    def _array(self, count: int) -> list[Any]:
        return [self.read() for _ in range(count)]

    def _map(self, count: int) -> dict[Any, Any]:
        return {self.read(): self.read() for _ in range(count)}

    def _bytes(self, length: int) -> bytes:
        end = self.index + length
        if end > len(self.data):
            raise MessagePackDecodeError("unexpected end of MessagePack payload")
        value = self.data[self.index:end]
        self.index = end
        return value

    def _u8(self) -> int:
        if self.index >= len(self.data):
            raise MessagePackDecodeError("unexpected end of MessagePack payload")
        value = self.data[self.index]
        self.index += 1
        return value

    def _u16(self) -> int:
        return int.from_bytes(self._bytes(2), "big")

    def _u32(self) -> int:
        return int.from_bytes(self._bytes(4), "big")

    def _u64(self) -> int:
        return int.from_bytes(self._bytes(8), "big")

    def _i8(self) -> int:
        return int.from_bytes(self._bytes(1), "big", signed=True)

    def _i16(self) -> int:
        return int.from_bytes(self._bytes(2), "big", signed=True)

    def _i32(self) -> int:
        return int.from_bytes(self._bytes(4), "big", signed=True)

    def _i64(self) -> int:
        return int.from_bytes(self._bytes(8), "big", signed=True)


def unpack_messagepack(data: bytes | bytearray | memoryview) -> Any:
    reader = _Reader(data)
    value = reader.read()
    if not reader.end:
        raise MessagePackDecodeError("trailing MessagePack bytes")
    return value


def decode_binary(data: bytes | bytearray | memoryview) -> BinaryDocument:
    raw = unpack_messagepack(data)
    if not isinstance(raw, dict):
        raise MessagePackDecodeError("FastParse binary payload must be a map")
    if raw.get("format") != "tsmp-binary":
        raise MessagePackDecodeError("FastParse binary payload has an invalid format marker")
    if raw.get("schemaVersion") != 1:
        raise MessagePackDecodeError(f"unsupported FastParse binary schema version: {raw.get('schemaVersion')}")

    nodes = [_decode_node(node) for node in raw.get("nodes", [])]
    return BinaryDocument(
        format=raw.get("format", ""),
        schema_version=int(raw.get("schemaVersion", 0)),
        language=raw.get("language", ""),
        has_errors=raw.get("hasErrors"),
        error_node_count=raw.get("errorNodeCount"),
        missing_node_count=raw.get("missingNodeCount"),
        error_byte_count=raw.get("errorByteCount"),
        nodes=nodes,
        node_count=int(raw.get("nodeCount", len(nodes))),
    )


def _decode_node(raw: Any) -> BinaryNode:
    if not isinstance(raw, dict):
        raise MessagePackDecodeError("FastParse binary node must be a map")
    return BinaryNode(
        id=raw.get("id"),
        parent_id=raw.get("parentId"),
        rule=raw.get("rule"),
        text=raw.get("text"),
        start_line=raw.get("startLine"),
        start_column=raw.get("startColumn"),
        end_line=raw.get("endLine"),
        end_column=raw.get("endColumn"),
        start_byte=raw.get("startByte"),
        end_byte=raw.get("endByte"),
        child_count=raw.get("childCount"),
        is_error=raw.get("isError"),
        is_missing=raw.get("isMissing"),
        has_error=raw.get("hasError"),
        children=[_decode_child(child) for child in raw.get("children", [])],
    )


def _decode_child(raw: Any) -> BinaryChild:
    if not isinstance(raw, dict):
        raise MessagePackDecodeError("FastParse binary child must be a map")
    return BinaryChild(rule=raw.get("rule"), text=raw.get("text"))
