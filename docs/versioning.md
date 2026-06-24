# Versioning

FastParser follows semantic versioning for the public .NET package once stable releases begin.

Preview releases use suffixes such as:

```text
0.1.0-preview.10
```

## Compatibility Surfaces

FastParser has several compatibility surfaces:

```text
NuGet package API       C# classes, enums, properties, and method signatures.
Native C ABI            fastparse_* symbols and native structs.
Binary output schema    MessagePack format documented in docs/binary_schema.md.
Grammar behavior        Tree-sitter grammar versions and node names.
```

## Patch Releases

Patch releases may:

- fix bugs;
- improve docs and examples;
- add non-breaking helper APIs;
- improve packaging and CI;
- add native platform fixes without changing contracts.

## Minor Releases

Minor releases may:

- add languages;
- add output fields;
- add new formats or options;
- add new binding APIs while keeping existing APIs compatible.

## Major Releases

Major releases are required for:

- removing or renaming public C# APIs;
- changing enum values;
- changing native ABI struct layout incompatibly;
- changing binary MessagePack schema incompatibly;
- changing default behavior in a way that can break existing consumers.

## Binary Schema

Binary output carries a schema version. Consumers should check it before assuming payload layout.

## Grammar Names

Tree-sitter grammar rule names are part of the practical contract for filtered extraction. Adding languages or upgrading grammars may add rule names. Removing or renaming commonly used rules should be treated as a compatibility risk and documented in release notes.
