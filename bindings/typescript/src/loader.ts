import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { NativeLoadError } from "./errors";

export function nativeFileName(): string {
  if (process.platform === "darwin") return "libfastparse.dylib";
  if (process.platform === "win32") return "fastparse.dll";
  return "libfastparse.so";
}

export function languageExtensionFileName(language: string): string {
  const canonical = canonicalLanguage(language);
  if (process.platform === "darwin") return `libfastparse_language_${canonical}.dylib`;
  if (process.platform === "win32") return `fastparse_language_${canonical}.dll`;
  return `libfastparse_language_${canonical}.so`;
}

export function runtimeId(): string {
  const platform = process.platform === "darwin" ? "osx" : process.platform === "win32" ? "win" : "linux";
  const arch = process.arch === "x64" ? "x64" : process.arch === "arm64" ? "arm64" : process.arch;
  return `${platform}-${arch}`;
}

export function canonicalLanguage(language: string): string {
  const canonical = language.trim().toLowerCase().replace(/-/g, "_");
  if (!canonical) throw new TypeError("language is required");
  return canonical;
}

export function resolveNativeLibrary(explicitPath?: string): string {
  const candidates = nativeLibraryCandidates(explicitPath);
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) return candidate;
  }
  throw new NativeLoadError(
    [
      "Unable to locate the native FastParse library.",
      `OS: ${os.platform()} ${os.release()}`,
      `Architecture: ${process.arch}`,
      "Set FASTPARSE_LIBRARY_PATH or install a package that includes native assets.",
      "Searched:",
      ...candidates.map((candidate) => `  - ${candidate}`)
    ].join("\n"),
    candidates
  );
}

export function resolveBundledLanguageExtension(language: string): string {
  const canonical = canonicalLanguage(language);
  const envName = `FASTPARSE_LANGUAGE_${canonical.toUpperCase()}_PATH`;
  const explicitPath = process.env[envName];
  if (explicitPath) return explicitPath;

  const candidates = bundledLanguageCandidates(canonical);
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) return candidate;
  }
  throw new NativeLoadError(
    [
      `Unable to locate bundled FastParse language extension '${canonical}'.`,
      `Install the matching package, for example: fastparse-language-${canonical.replace(/_/g, "-")}`,
      `Or set ${envName}.`,
      "Searched:",
      ...candidates.map((candidate) => `  - ${candidate}`)
    ].join("\n"),
    candidates
  );
}

function nativeLibraryCandidates(explicitPath?: string): string[] {
  if (explicitPath) return [explicitPath];
  const envPath = process.env.FASTPARSE_LIBRARY_PATH || process.env.TSMP_LIBRARY_PATH;
  if (envPath) return [envPath];

  const fileName = nativeFileName();
  const rid = runtimeId();
  const roots = ancestorDirectories(__dirname);
  roots.push(process.cwd());
  return unique([
    ...roots.flatMap((root) => [
      path.join(root, fileName),
      path.join(root, "bin", fileName),
      path.join(root, "native", rid, fileName),
      path.join(root, "runtimes", rid, "native", fileName),
      path.join(root, "..", "..", "bin", fileName)
    ])
  ]);
}

function bundledLanguageCandidates(language: string): string[] {
  const fileName = languageExtensionFileName(language);
  const rid = runtimeId();
  const roots = ancestorDirectories(__dirname);
  roots.push(process.cwd());
  return unique(
    roots.flatMap((root) => [
      path.join(root, "fastparse", "languages", language, "native", rid, fileName),
      path.join(root, "fastparse", "languages", language, "runtimes", rid, "native", fileName),
      path.join(root, "node_modules", `fastparse-language-${language.replace(/_/g, "-")}`, "native", rid, fileName),
      path.join(root, "node_modules", `fastparse-language-${language.replace(/_/g, "-")}`, "runtimes", rid, "native", fileName),
      path.join(root, "runtimes", rid, "native", fileName),
      path.join(root, "native", rid, fileName),
      path.join(root, fileName)
    ])
  );
}

function ancestorDirectories(start: string): string[] {
  const directories: string[] = [];
  let current = path.resolve(start);
  while (true) {
    directories.push(current);
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return directories;
}

function unique(values: string[]): string[] {
  return Array.from(new Set(values));
}
