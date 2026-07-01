# Changelog

All notable changes to FastParse will be documented here.

This project follows semantic versioning once the first stable release is published.

## 0.1.0

### Added

- FastParse language extension packaging for `java-frameworks`.
- FastParse language extension packaging for `javaswing`.
- Published package support for `fastparse-language-java-frameworks` on PyPI.
- Published package support for `FastParser.Language.JavaFrameworks` on NuGet.
- Release workflow support for `FastParser.Language.JavaSwing` on NuGet.
- Framework evidence grammar nodes for imports, annotations, and JDBC connection string literals.
- Framework family query captures for Spring, Spring Security, Hibernate/JPA, JDBC, Axis/Axis2, JAXB, JasperReports, BouncyCastle, JJWT, Springfox/Swagger, XStream, Oracle/SQL Server drivers, Lombok, Jackson/Gson, logging, Apache libraries, Servlet, Bean Validation, JUnit/Mockito, AspectJ, JOSE/Jasypt, and related enterprise Java libraries.
- Public-safe corpus coverage for framework imports, modern annotations, negative Java annotation behavior, and baseline Java parsing.
- Public support matrix for Java Frameworks detection under `grammars/tree-sitter-java-frameworks/docs/rule-catalogs/framework_support_matrix.md`.

### Changed

- Release workflow now builds, publishes, and smoke-tests Java Frameworks language packages across Linux x64, Windows x64, macOS x64, and macOS arm64.
- Release workflow now builds, publishes, and smoke-tests the JavaSwing NuGet language package across Linux x64, Windows x64, macOS x64, and macOS arm64.
- Language extension NuGet packages now use NuGet-compatible OPC metadata and Apache 2.0 license URL metadata.
- Documentation now distinguishes grammar-level evidence from query-level framework classification.

### Validation

- `tree-sitter test`: 5/5 corpus cases passing.
- `v0.1.0-preview.32`: public PyPI and NuGet publication succeeded with post-publish smoke tests on all supported platforms.

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
