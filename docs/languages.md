# Language Strategy

TSMP is designed to support multiple Tree-sitter grammars while keeping the C ABI stable.

For the package-manager-first extension model, read [Language Extensions](language_extensions.md).

The public API does not change when a language is added. Callers select the language through:

```c
TsmpOptions options = {
    .language = "java"
};
```

## Initial Language Set

Current lab build:

| Public name | Grammar | Status |
|---|---|---|
| `java` | `tree-sitter-java` | Implemented |

Desired next language set:

| Public name | Grammar | Expected function |
|---|---|---|
| `csharp` | `tree-sitter-c-sharp` | `tree_sitter_c_sharp()` |
| `rust` | `tree-sitter-rust` | `tree_sitter_rust()` |
| `python` | `tree-sitter-python` | `tree_sitter_python()` |

## Public Language Names

Language names should be stable, lowercase, and binding-friendly.

Recommended names:

```text
java
csharp
rust
python
```

Avoid symbols that are awkward in CLI flags, JSON, package names, or bindings, such as:

```text
c#
CSharp
tree-sitter-c-sharp
```

Aliases can be added later, but the canonical name should be simple.

## Grammar Layout

Each grammar should live under:

```text
grammars/tree-sitter-<grammar-name>/
```

Required generated source:

```text
src/parser.c
```

Optional scanner:

```text
src/scanner.c
src/scanner.cc
```

The current build script handles `scanner.c`. C++ scanners require additional compiler/linker handling and should be explicitly supported when needed.

## Registry

Current language registry:

[src/tsmp_languages.c](../src/tsmp_languages.c)

Current pattern:

```c
typedef struct {
    const char *name;
    TsmpLanguageFn language;
} TsmpLanguageEntry;

extern const TSLanguage *tree_sitter_java(void);

static const TsmpLanguageEntry TSMP_LANGUAGES[] = {
    { "java", tree_sitter_java },
    { NULL, NULL }
};
```

Adding `rust` would look like:

```c
extern const TSLanguage *tree_sitter_rust(void);

static const TsmpLanguageEntry TSMP_LANGUAGES[] = {
    { "java", tree_sitter_java },
    { "rust", tree_sitter_rust },
    { NULL, NULL }
};
```

## Build Inclusion

The build should compile only the grammars intentionally included in the distribution.

Two possible strategies:

### Static Registry

The source registry is edited explicitly when adding a language.

Pros:

- Simple.
- Deterministic.
- Easy to audit.

Cons:

- Requires rebuild for each language set.

### Generated Registry

CMake or a script generates the registry from a manifest.

Example manifest:

```json
{
  "languages": [
    {
      "name": "java",
      "grammarPath": "grammars/tree-sitter-java",
      "function": "tree_sitter_java"
    }
  ]
}
```

Pros:

- Better for many languages.
- Easy to make language profiles.

Cons:

- More build-system complexity.

Recommendation: keep static registry for the lab, move to manifest generation when adding multiple release profiles.

## Release Profiles

The library can support different profiles:

```text
tsmp-java
tsmp-jvm        java + csharp
tsmp-corelangs  java + csharp + rust + python
tsmp-full       all supported grammars
```

Profiles keep package size under control while preserving extensibility.

## Rule Names

Rule names come from each grammar. TSMP does not normalize rule names.

Example Java rules:

```text
program
class_declaration
method_declaration
constructor_declaration
method_invocation
field_declaration
```

Callers should use exploration mode to discover rule names:

```text
format = JSON
include_rules = NULL
fields = TSMP_FIELD_RULE
```

Then production code should filter:

```text
include_rules = "class_declaration|method_declaration"
```

## Tests Required Per Language

Every added language should include:

- One small sample source file.
- JSON default exploration test.
- Filtered rules test.
- CSV output test.
- Stats count test.
- Invalid language regression remains passing.
- Bulk smoke test if a real corpus exists.

## Open Decisions

- Whether to support runtime-loaded grammars in the future.
- Whether to support aliases such as `cs` for `csharp`.
- How to handle grammars with C++ scanners.
- Whether language profiles are separate packages or one package with optional builds.
