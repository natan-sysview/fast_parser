# Release Checklist

Use this checklist before publishing a GitHub release.

## Version

- [ ] Decide release version, for example `v0.1.0`.
- [ ] Align README status section.
- [ ] Confirm `fastparse_version()` output.
- [ ] Confirm binary `schemaVersion`.
- [ ] Update [CHANGELOG.md](../CHANGELOG.md).

## Build

- [ ] Clean build directory.
- [ ] Build native library with `./compila_lib.sh`.
- [ ] Confirm expected library exists under `bin/`.
- [ ] Build C# binding/examples.
- [ ] Run C# binding contract tests.
- [ ] Run Python tests.
- [ ] Run C smoke tests.

Commands:

```bash
./compila_lib.sh
python3 -m unittest discover -s tests -v
ctest --test-dir build --output-on-failure
dotnet build examples/csharp/01_parse_string/FastParse.ParseStringExample.csproj
dotnet build examples/csharp/03_inventory_to_sqlite/FastParse.InventoryToSqliteExample.csproj
dotnet test tests/csharp/FastParse.Tests/FastParse.Tests.csproj --configuration Release
```

## Docs

- [ ] README quick start works from a fresh clone.
- [ ] C API docs match `include/fastparse.h`.
- [ ] Binary schema docs match actual MessagePack output.
- [ ] Python example works.
- [ ] C# example works.
- [ ] AI agent guide is current.
- [ ] Third-party notices are current.

## Package Contents

Build release archives locally:

```bash
python3 scripts/package_release.py --version 0.1.0-preview.10
```

GitHub Actions release artifacts:

```text
.github/workflows/release.yml
```

Expected release archives:

```text
fastparse-<version>-linux-x64.tar.gz
fastparse-<version>-macos-x64.tar.gz
fastparse-<version>-macos-arm64.tar.gz
fastparse-<version>-windows-x64.zip
FastParser.<version>.nupkg
FastParser.<version>.snupkg
SHA256SUMS.txt
```

Release source package should include:

```text
include/
src/
grammars/
vendor/
bindings/
examples/
tests/
docs/
CMakeLists.txt
compila_lib.sh
README.md
LICENSE
THIRD_PARTY_NOTICES.md
CHANGELOG.md
```

Release source package should not include:

```text
build/
bin/
data/*.sqlite
data/*.sqlite-shm
data/*.sqlite-wal
examples/**/bin/
examples/**/obj/
bindings/**/bin/
bindings/**/obj/
__pycache__/
.DS_Store
```

## Smoke Tests From Fresh Clone

```bash
./compila_lib.sh
python3 examples/python/01_parse_string/parse_string.py --summary
dotnet run --project examples/csharp/01_parse_string/FastParse.ParseStringExample.csproj
```

## GitHub Release

- [ ] Create tag.
- [ ] Attach source archive.
- [ ] Attach native binaries when available.
- [ ] Attach NuGet package and symbols package.
- [ ] Include supported platforms in release notes.
- [ ] Include known limitations.

## Current Known Limitations

- Java grammar only.
- Binary schema is version 1.
- `pretty` option is reserved.
