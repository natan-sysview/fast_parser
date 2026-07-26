import { decode } from "@msgpack/msgpack";

export interface BinaryChild {
  rule?: string;
  text?: Uint8Array;
}

export interface BinaryNode {
  id?: number;
  parentId?: number | null;
  fieldName?: string | null;
  childIndex?: number;
  isNamed?: boolean;
  depth?: number;
  rule?: string;
  text?: Uint8Array;
  startLine?: number;
  startColumn?: number;
  endLine?: number;
  endColumn?: number;
  startByte?: number;
  endByte?: number;
  childCount?: number;
  isError?: boolean;
  isMissing?: boolean;
  hasError?: boolean;
  children?: BinaryChild[];
}

export interface BinaryDocument {
  format: "tsmp-binary" | "fastparse-query-binary";
  schemaVersion: number;
  language: string;
  nodes?: BinaryNode[];
  matches?: unknown[];
  nodeCount?: number;
  matchCount?: number;
  captureCount?: number;
  hasErrors?: boolean;
  errorNodeCount?: number;
  missingNodeCount?: number;
  errorByteCount?: number;
}

export function decodeBinary(data: Buffer | Uint8Array): BinaryDocument {
  const document = decode(data) as BinaryDocument;
  if (!document || typeof document !== "object") {
    throw new TypeError("FastParse binary payload must decode to an object.");
  }
  if (document.schemaVersion !== 1) {
    throw new RangeError(`unsupported FastParse binary schema version: ${document.schemaVersion}`);
  }
  if (document.format !== "tsmp-binary" && document.format !== "fastparse-query-binary") {
    throw new TypeError(`invalid FastParse binary marker: ${String(document.format)}`);
  }
  return document;
}
