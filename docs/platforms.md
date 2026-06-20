# Platform Strategy

TSMP must be portable across macOS, Linux, and Windows. The core is written in C and exposes a small C ABI so higher-level bindings can load it through FFI.

## Supported Targets

Initial target matrix:

| Platform | Architecture | Artifact |
|---|---:|---|
| macOS | arm64 | `libfastparse.dylib` |
| macOS | x64 | `libfastparse.dylib` |
| Linux | x64 | `libfastparse.so` |
| Linux | arm64 | `libfastparse.so` |
| Windows | x64 | `fastparse.dll` plus import library when needed |

The current lab build has been validated on macOS arm64.

## Build System Direction

Use CMake as the primary portable build system.

Reasons:

- Native support for macOS, Linux, and Windows.
- Good fit for shared libraries.
- Easier integration with CI matrix builds.
- Common path for packaging headers, libraries, and examples.
- Better long-term maintainability than OS-specific shell scripts.

The existing `compila_lib.sh` is a local development helper over CMake.

## Cross-Compilation Policy

Cross-compilation is not the primary strategy.

C can be cross-compiled, but doing it reliably across macOS, Linux, Windows, x64, and arm64 requires platform-specific toolchains, SDKs, and linker behavior. For this project, native CI builds are preferred.

Preferred release flow:

```text
macOS runner   -> macOS artifacts
Linux runner   -> Linux artifacts
Windows runner -> Windows artifacts
```

Cross-compilation may be introduced later for specific targets, but it should not be required for normal releases.

## Dynamic Library Names

Use a stable logical package name: `fastparse`.

Recommended output names:

```text
macOS   libfastparse.dylib
Linux   libfastparse.so
Windows fastparse.dll
```

The lab now emits `libfastparse.dylib` on macOS.

## Exported ABI

The dynamic library should export only:

```c
tsmp_version
tsmp_parse
tsmp_result_free
```

FastParse-branded aliases are also exported:

```c
fastparse_version
fastparse_parse
fastparse_result_free
```

Internal symbols should remain hidden.

Current macOS build uses:

```text
-fvisibility=hidden
-DTSMP_BUILD_SHARED
-DTREE_SITTER_HIDE_SYMBOLS
```

Windows will need equivalent export control through `__declspec(dllexport)` from `TSMP_API`.

The build should also enforce the public ABI at linker level:

```text
macOS   -exported_symbols_list exports/tsmp_macos.exports
Linux   --version-script exports/tsmp_linux.map
Windows .def file or explicit dllexport policy
```

## Runtime And Grammar Linking

The release library should statically compile:

- TSMP core.
- Tree-sitter runtime.
- Selected grammar parser sources.

This avoids requiring users to install Tree-sitter separately.

The package should not include development folders such as:

- `node_modules`
- `venv`
- grammar test suites
- build folders
- object files

## CI Direction

Recommended CI jobs:

```text
build-macos-arm64
build-macos-x64
build-linux-x64
build-linux-arm64
build-windows-x64
```

Each job should:

1. Configure with CMake.
2. Build the shared library.
3. Run C/Python contract tests.
4. Validate exported symbols.
5. Package the artifact.

## Open Decisions

- Whether to ship static libraries in addition to shared libraries.
- Whether to keep macOS universal binaries or separate arm64/x64 packages.
- Whether Windows package includes only `fastparse.dll` or also a `.lib` import library.
