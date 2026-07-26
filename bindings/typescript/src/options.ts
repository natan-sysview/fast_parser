import { FieldName, Normalization, NormalizationName, OutputFormat, OutputFormatName } from "./constants";

export type IncludeRules = string | string[] | null;

export interface ParseOptions {
  language?: string;
  outputFormat?: OutputFormat | OutputFormatName;
  includeRules?: IncludeRules;
  fields?: number | FieldName | Array<FieldName | number> | null;
  includeTokens?: boolean;
  pretty?: boolean;
  normalization?: Normalization | NormalizationName;
}

export interface QueryOptions {
  language?: string;
  outputFormat?: OutputFormat | OutputFormatName;
  fields?: number | FieldName | Array<FieldName | number> | null;
  maxMatches?: number;
  maxCaptures?: number;
  includePattern?: boolean;
  pretty?: boolean;
  normalization?: Normalization | NormalizationName;
}

export interface FastParseClientOptions {
  libraryPath?: string;
}

export interface ParseSummary {
  outputLength: number;
  nodeCount: number;
  outputFormat: OutputFormatName;
}

export interface LanguageExtensionLoadResult {
  language: string;
  displayName: string;
}

export function includeRulesValue(rules: IncludeRules | undefined): string | null {
  if (rules === undefined || rules === null) return null;
  if (Array.isArray(rules)) {
    const joined = rules.filter(Boolean).join("|");
    return joined.length > 0 ? joined : null;
  }
  return rules.length > 0 ? rules : null;
}
