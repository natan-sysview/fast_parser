import { Buffer } from "node:buffer";
import { fieldMask, normalizationValue, outputFormatName, outputFormatValue } from "./constants";
import { FastParseError } from "./errors";
import { canonicalLanguage, resolveBundledLanguageExtension, resolveNativeLibrary } from "./loader";
import { FastParseClientOptions, includeRulesValue, LanguageExtensionLoadResult, ParseOptions, ParseSummary, QueryOptions } from "./options";
import { ParseResult } from "./result";

// koffi ships its own runtime. Import through require to keep the generated CommonJS output Electron-friendly.
// eslint-disable-next-line @typescript-eslint/no-var-requires
const koffi: any = require("koffi");

const TsmpOptions = koffi.struct("TsmpOptions", {
  language: "str",
  format: "int",
  include_rules: "str",
  fields: "uint32_t",
  include_tokens: "int",
  pretty: "int"
});

const TsmpOptionsV2 = koffi.struct("TsmpOptionsV2", {
  language: "str",
  format: "int",
  include_rules: "str",
  fields: "uint32_t",
  include_tokens: "int",
  pretty: "int",
  normalization: "int"
});

const TsmpQueryOptions = koffi.struct("TsmpQueryOptions", {
  language: "str",
  format: "int",
  fields: "uint32_t",
  max_matches: "size_t",
  max_captures: "size_t",
  include_pattern: "int",
  pretty: "int",
  normalization: "int"
});

const TsmpResult = koffi.struct("TsmpResult", {
  status: "int",
  data: "void *",
  length: "size_t",
  node_count: "size_t",
  error_message: "void *"
});

const FastParseLanguageLoadResult = koffi.struct("FastParseLanguageLoadResult", {
  status: "int",
  language: "void *",
  display_name: "void *",
  error_message: "void *"
});

interface NativeResult {
  status: number;
  data: unknown;
  length: number | bigint;
  node_count: number | bigint;
  error_message: unknown;
}

interface NativeLanguageLoadResult {
  status: number;
  language: unknown;
  display_name: unknown;
  error_message: unknown;
}

export class FastParseClient {
  readonly libraryPath: string;
  private readonly lib: any;
  private readonly versionFn: () => string;
  private readonly parseFn: (source: Buffer | null, sourceLength: number, options: unknown, outResult: unknown) => number;
  private readonly parseV2Fn?: (source: Buffer | null, sourceLength: number, options: unknown, outResult: unknown) => number;
  private readonly queryFn: (source: Buffer | null, sourceLength: number, query: Buffer | null, queryLength: number, options: unknown, outResult: unknown) => number;
  private readonly resultFreeFn: (result: unknown) => void;
  private readonly loadLanguageExtensionFn: (path: string, outResult: unknown) => number;
  private readonly languageAvailableFn: (language: string) => number;
  private readonly languageLoadResultFreeFn: (result: unknown) => void;

  constructor(options: FastParseClientOptions = {}) {
    this.libraryPath = resolveNativeLibrary(options.libraryPath);
    this.lib = koffi.load(this.libraryPath);
    this.versionFn = this.loadFunction("fastparse_version", "tsmp_version", "str", []);
    this.parseFn = this.loadFunction(
      "fastparse_parse",
      "tsmp_parse",
      "int",
      ["void *", "size_t", koffi.pointer(TsmpOptions), koffi.out(koffi.pointer(TsmpResult))]
    );
    this.parseV2Fn = this.tryLoadFunction(
      "fastparse_parse_v2",
      "tsmp_parse_v2",
      "int",
      ["void *", "size_t", koffi.pointer(TsmpOptionsV2), koffi.out(koffi.pointer(TsmpResult))]
    );
    this.queryFn = this.loadFunction(
      "fastparse_query",
      "tsmp_query",
      "int",
      ["void *", "size_t", "void *", "size_t", koffi.pointer(TsmpQueryOptions), koffi.out(koffi.pointer(TsmpResult))]
    );
    this.resultFreeFn = this.loadFunction("fastparse_result_free", "tsmp_result_free", "void", [koffi.pointer(TsmpResult)]);
    this.loadLanguageExtensionFn = this.requiredFunction(
      "fastparse_load_language_extension",
      "int",
      ["str", koffi.out(koffi.pointer(FastParseLanguageLoadResult))]
    );
    this.languageAvailableFn = this.requiredFunction("fastparse_language_available", "int", ["str"]);
    this.languageLoadResultFreeFn = this.requiredFunction(
      "fastparse_language_load_result_free",
      "void",
      [koffi.pointer(FastParseLanguageLoadResult)]
    );
  }

  get version(): string {
    return this.versionFn();
  }

  languageAvailable(language: string): boolean {
    return this.languageAvailableFn(language) !== 0;
  }

  loadLanguageExtension(extensionPath: string): LanguageExtensionLoadResult {
    const result = {} as NativeLanguageLoadResult;
    const status = this.loadLanguageExtensionFn(extensionPath, result);
    try {
      if (status !== 0 || result.status !== 0) {
        throw new FastParseError(
          `fastparse_load_language_extension failed with status ${status}/${result.status}: ${this.nativeString(result.error_message) || "no error detail"}`,
          status,
          result.status
        );
      }
      return {
        language: this.nativeString(result.language),
        displayName: this.nativeString(result.display_name)
      };
    } finally {
      this.languageLoadResultFreeFn(result);
    }
  }

  loadBundledLanguage(language: string): LanguageExtensionLoadResult {
    const canonical = canonicalLanguage(language);
    if (this.languageAvailable(canonical)) {
      return { language: canonical, displayName: canonical };
    }
    const extensionPath = resolveBundledLanguageExtension(canonical);
    const result = this.loadLanguageExtension(extensionPath);
    if (!this.languageAvailable(canonical)) {
      throw new FastParseError(`extension loaded ${result.language}, but ${canonical} is still unavailable`);
    }
    return result;
  }

  parseBytes(source: Buffer | Uint8Array | ArrayBuffer, options: ParseOptions = {}): ParseResult {
    const native = this.parseNative(source, options, true);
    return new ParseResult(native.data, native.nodeCount, native.outputFormat);
  }

  parseBytesSummary(source: Buffer | Uint8Array | ArrayBuffer, options: ParseOptions = {}): ParseSummary {
    const native = this.parseNative(source, options, false);
    return {
      outputLength: native.outputLength,
      nodeCount: native.nodeCount,
      outputFormat: native.outputFormat
    };
  }

  parseText(source: string, options: ParseOptions = {}, encoding: BufferEncoding = "utf8"): ParseResult {
    return this.parseBytes(Buffer.from(source, encoding), options);
  }

  parseTextSummary(source: string, options: ParseOptions = {}, encoding: BufferEncoding = "utf8"): ParseSummary {
    return this.parseBytesSummary(Buffer.from(source, encoding), options);
  }

  queryBytes(source: Buffer | Uint8Array | ArrayBuffer, query: string | Buffer | Uint8Array, options: QueryOptions = {}): ParseResult {
    const native = this.queryNative(source, query, options, true);
    return new ParseResult(native.data, native.nodeCount, native.outputFormat);
  }

  queryBytesSummary(source: Buffer | Uint8Array | ArrayBuffer, query: string | Buffer | Uint8Array, options: QueryOptions = {}): ParseSummary {
    const native = this.queryNative(source, query, options, false);
    return {
      outputLength: native.outputLength,
      nodeCount: native.nodeCount,
      outputFormat: native.outputFormat
    };
  }

  queryText(source: string, query: string, options: QueryOptions = {}, encoding: BufferEncoding = "utf8"): ParseResult {
    return this.queryBytes(Buffer.from(source, encoding), query, options);
  }

  queryTextSummary(source: string, query: string, options: QueryOptions = {}, encoding: BufferEncoding = "utf8"): ParseSummary {
    return this.queryBytesSummary(Buffer.from(source, encoding), query, options);
  }

  private parseNative(source: Buffer | Uint8Array | ArrayBuffer, options: ParseOptions, copyData: boolean): {
    data: Buffer;
    nodeCount: number;
    outputLength: number;
    outputFormat: ReturnType<typeof outputFormatName>;
  } {
    const sourceBuffer = toBuffer(source);
    const format = outputFormatValue(options.outputFormat);
    const result = {} as NativeResult;
    const language = options.language ?? "java";
    const includeRules = includeRulesValue(options.includeRules);
    let status: number;

    if (this.parseV2Fn) {
      const nativeOptions = {
        language,
        format,
        include_rules: includeRules,
        fields: fieldMask(options.fields),
        include_tokens: options.includeTokens ? 1 : 0,
        pretty: options.pretty ? 1 : 0,
        normalization: normalizationValue(options.normalization)
      };
      status = this.parseV2Fn(sourceBuffer.length > 0 ? sourceBuffer : null, sourceBuffer.length, nativeOptions, result);
    } else {
      if (normalizationValue(options.normalization) !== 0) {
        throw new FastParseError("native FastParse library does not support explicit normalization options");
      }
      const nativeOptions = {
        language,
        format,
        include_rules: includeRules,
        fields: fieldMask(options.fields),
        include_tokens: options.includeTokens ? 1 : 0,
        pretty: options.pretty ? 1 : 0
      };
      status = this.parseFn(sourceBuffer.length > 0 ? sourceBuffer : null, sourceBuffer.length, nativeOptions, result);
    }

    return this.consumeResult(result, status, format, copyData, "fastparse_parse");
  }

  private queryNative(source: Buffer | Uint8Array | ArrayBuffer, query: string | Buffer | Uint8Array, options: QueryOptions, copyData: boolean): {
    data: Buffer;
    nodeCount: number;
    outputLength: number;
    outputFormat: ReturnType<typeof outputFormatName>;
  } {
    const sourceBuffer = toBuffer(source);
    const queryBuffer = typeof query === "string" ? Buffer.from(query, "utf8") : toBuffer(query);
    const format = outputFormatValue(options.outputFormat);
    const result = {} as NativeResult;
    const nativeOptions = {
      language: options.language ?? "java",
      format,
      fields: fieldMask(options.fields),
      max_matches: Math.max(0, Math.trunc(options.maxMatches ?? 0)),
      max_captures: Math.max(0, Math.trunc(options.maxCaptures ?? 0)),
      include_pattern: options.includePattern === false ? 0 : 1,
      pretty: options.pretty ? 1 : 0,
      normalization: normalizationValue(options.normalization)
    };

    const status = this.queryFn(
      sourceBuffer.length > 0 ? sourceBuffer : null,
      sourceBuffer.length,
      queryBuffer.length > 0 ? queryBuffer : null,
      queryBuffer.length,
      nativeOptions,
      result
    );
    return this.consumeResult(result, status, format, copyData, "fastparse_query");
  }

  private consumeResult(result: NativeResult, status: number, format: number, copyData: boolean, operation: string): {
    data: Buffer;
    nodeCount: number;
    outputLength: number;
    outputFormat: ReturnType<typeof outputFormatName>;
  } {
    try {
      if (status !== 0 || result.status !== 0) {
        throw new FastParseError(
          `${operation} failed with status ${status}/${result.status}: ${this.nativeString(result.error_message) || "no error detail"}`,
          status,
          result.status
        );
      }

      const outputLength = Number(result.length ?? 0);
      let data = Buffer.alloc(0);
      if (copyData && outputLength > 0 && result.data) {
        data = Buffer.from(koffi.decode(result.data, "uint8_t", outputLength));
      }
      return {
        data,
        nodeCount: Number(result.node_count ?? 0),
        outputLength,
        outputFormat: outputFormatName(format)
      };
    } finally {
      this.resultFreeFn(result);
    }
  }

  private nativeString(pointer: unknown): string {
    if (!pointer) return "";
    return koffi.decode(pointer, "char", -1) ?? "";
  }

  private loadFunction(preferred: string, fallback: string, resultType: unknown, argTypes: unknown[]): any {
    return this.tryFunction(preferred, resultType, argTypes) ?? this.requiredFunction(fallback, resultType, argTypes);
  }

  private tryLoadFunction(preferred: string, fallback: string, resultType: unknown, argTypes: unknown[]): any | undefined {
    return this.tryFunction(preferred, resultType, argTypes) ?? this.tryFunction(fallback, resultType, argTypes);
  }

  private requiredFunction(name: string, resultType: unknown, argTypes: unknown[]): any {
    const fn = this.tryFunction(name, resultType, argTypes);
    if (!fn) throw new FastParseError(`native FastParse symbol not found: ${name}`);
    return fn;
  }

  private tryFunction(name: string, resultType: unknown, argTypes: unknown[]): any | undefined {
    try {
      return this.lib.func(name, resultType, argTypes);
    } catch {
      return undefined;
    }
  }
}

function toBuffer(source: Buffer | Uint8Array | ArrayBuffer): Buffer {
  if (Buffer.isBuffer(source)) return source;
  if (source instanceof ArrayBuffer) return Buffer.from(source);
  return Buffer.from(source.buffer, source.byteOffset, source.byteLength);
}

export const FastParse = FastParseClient;
