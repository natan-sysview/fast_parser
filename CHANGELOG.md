# Changelog

All notable changes to FastParse will be documented here.

This project follows semantic versioning once the first stable release is published.

## 0.1.0-preview.8

### Added

- SourceLink metadata for the C# NuGet package.
- Portable PDBs and NuGet symbols package (`.snupkg`) for C# debugging.
- C# binding contract tests for JSON, CSV, binary, stats, explicit native loading, and error handling.
- NuGet package validation for XML docs, PDBs, native RID assets, AI docs, and symbols package contents.

### Changed

- Release workflow now publishes the symbols package alongside the main NuGet package.
- Release workflow runs C# binding tests before packaging artifacts.

## 0.1.0-preview

Initial public preview.

### Added

- Native C parsing API with `fastparse_*` public symbols.
- Compatibility `tsmp_*` symbols.
- Java grammar support.
- JSON output.
- CSV output.
- MessagePack binary output with schema version 1.
- Stats output for node counting.
- Rule filtering through `include_rules`.
- Field filtering through bit masks.
- Python binding.
- C# binding.
- Python examples.
- C# examples.
- SQLite inventory lab example.
- Documentation for contracts, binary schema, bindings, packaging, and AI agent integration.
