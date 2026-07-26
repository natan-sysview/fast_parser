import { BinaryDocument, decodeBinary } from "./binary";
import { OutputFormatName } from "./constants";

export class ParseResult {
  readonly data: Buffer;
  readonly nodeCount: number;
  readonly outputFormat: OutputFormatName;

  constructor(data: Buffer, nodeCount: number, outputFormat: OutputFormatName) {
    this.data = data;
    this.nodeCount = nodeCount;
    this.outputFormat = outputFormat;
  }

  text(encoding: BufferEncoding = "utf8"): string {
    return this.data.toString(encoding);
  }

  json<T = unknown>(): T {
    return JSON.parse(this.text()) as T;
  }

  binaryDocument(): BinaryDocument {
    return decodeBinary(this.data);
  }
}
