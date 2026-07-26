export enum OutputFormat {
  Json = 1,
  Csv = 2,
  Stats = 3,
  Binary = 4,
  Diagnostics = 5
}

export enum Normalization {
  AutoSafe = 0,
  None = 1,
  CobolFixedLegacy = 2
}

export enum NativeStatus {
  Ok = 0,
  InvalidArgument = 1,
  UnsupportedLanguage = 2,
  ParseFailed = 3,
  Io = 4,
  UnsupportedFormat = 5,
  OutOfMemory = 6,
  ExtensionLoad = 7,
  QueryCompile = 8,
  QueryExecute = 9
}

export const Field = {
  Id: 1 << 0,
  ParentId: 1 << 1,
  Rule: 1 << 2,
  Text: 1 << 3,
  Range: 1 << 4,
  ByteRange: 1 << 5,
  ChildCount: 1 << 6,
  Children: 1 << 7,
  Diagnostics: 1 << 8,
  CaptureName: 1 << 9,
  PatternIndex: 1 << 10,
  FieldName: 1 << 11,
  ChildIndex: 1 << 12,
  Named: 1 << 13,
  Depth: 1 << 14,
  All: 0xffffffff
} as const;

export type FieldValue = typeof Field[keyof typeof Field];

export type OutputFormatName = "json" | "csv" | "stats" | "binary" | "msgpack" | "diagnostics";
export type FieldName =
  | "id"
  | "parent_id"
  | "parent"
  | "rule"
  | "text"
  | "range"
  | "byte_range"
  | "bytes"
  | "child_count"
  | "children"
  | "diagnostics"
  | "capture_name"
  | "capture"
  | "name"
  | "pattern_index"
  | "pattern"
  | "field_name"
  | "field"
  | "child_index"
  | "named"
  | "is_named"
  | "depth"
  | "all";
export type NormalizationName = "auto" | "auto_safe" | "safe" | "none" | "off" | "cobol_fixed_legacy" | "cobol";

export function outputFormatValue(format: OutputFormat | OutputFormatName | undefined): OutputFormat {
  if (format === undefined) return OutputFormat.Json;
  if (typeof format === "number") return format;
  const normalized = format.trim().toLowerCase().replace(/-/g, "_");
  switch (normalized) {
    case "json":
      return OutputFormat.Json;
    case "csv":
      return OutputFormat.Csv;
    case "stats":
      return OutputFormat.Stats;
    case "binary":
    case "msgpack":
      return OutputFormat.Binary;
    case "diagnostics":
      return OutputFormat.Diagnostics;
    default:
      throw new RangeError(`unknown FastParse output format: ${format}`);
  }
}

export function outputFormatName(format: OutputFormat): OutputFormatName {
  switch (format) {
    case OutputFormat.Json:
      return "json";
    case OutputFormat.Csv:
      return "csv";
    case OutputFormat.Stats:
      return "stats";
    case OutputFormat.Binary:
      return "binary";
    case OutputFormat.Diagnostics:
      return "diagnostics";
    default:
      return `format_${format}` as OutputFormatName;
  }
}

export function normalizationValue(normalization: Normalization | NormalizationName | undefined): Normalization {
  if (normalization === undefined) return Normalization.AutoSafe;
  if (typeof normalization === "number") return normalization;
  const normalized = normalization.trim().toLowerCase().replace(/-/g, "_");
  switch (normalized) {
    case "auto":
    case "auto_safe":
    case "safe":
      return Normalization.AutoSafe;
    case "none":
    case "off":
      return Normalization.None;
    case "cobol":
    case "cobol_fixed_legacy":
      return Normalization.CobolFixedLegacy;
    default:
      throw new RangeError(`unknown FastParse normalization: ${normalization}`);
  }
}

export function fieldMask(fields?: number | FieldName | Array<FieldName | number> | null): number {
  if (fields === undefined || fields === null) return 0;
  if (typeof fields === "number") return fields === Field.All ? 0 : fields;
  const items = Array.isArray(fields) ? fields : fields.split(",");
  let mask = 0;
  for (const item of items) {
    if (typeof item === "number") {
      if (item === Field.All) return 0;
      mask |= item;
      continue;
    }
    const normalized = item.trim().toLowerCase().replace(/-/g, "_");
    if (!normalized) continue;
    switch (normalized) {
      case "id":
        mask |= Field.Id;
        break;
      case "parent":
      case "parent_id":
        mask |= Field.ParentId;
        break;
      case "rule":
        mask |= Field.Rule;
        break;
      case "text":
        mask |= Field.Text;
        break;
      case "range":
        mask |= Field.Range;
        break;
      case "byte_range":
      case "bytes":
        mask |= Field.ByteRange;
        break;
      case "child_count":
        mask |= Field.ChildCount;
        break;
      case "children":
        mask |= Field.Children;
        break;
      case "diagnostics":
        mask |= Field.Diagnostics;
        break;
      case "capture":
      case "capture_name":
      case "name":
        mask |= Field.CaptureName;
        break;
      case "pattern":
      case "pattern_index":
        mask |= Field.PatternIndex;
        break;
      case "field":
      case "field_name":
        mask |= Field.FieldName;
        break;
      case "child_index":
        mask |= Field.ChildIndex;
        break;
      case "named":
      case "is_named":
        mask |= Field.Named;
        break;
      case "depth":
        mask |= Field.Depth;
        break;
      case "all":
        return 0;
      default:
        throw new RangeError(`unknown FastParse field: ${item}`);
    }
  }
  return mask;
}
