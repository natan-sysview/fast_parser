# GitHub Publish Guide

Target repository:

```text
https://github.com/natan-sysview/fast_parser
```

## Recommended First Push

From a clean checkout of the GitHub repository:

```bash
git clone https://github.com/natan-sysview/fast_parser.git
cd fast_parser
```

Copy the prepared FastParse source into that checkout, then verify ignored files:

```bash
git status --short
```

Do not commit generated files:

```text
build/
bin/
data/*.sqlite
data/*.sqlite-shm
data/*.sqlite-wal
data/*benchmark*.json
examples/**/bin/
examples/**/obj/
bindings/**/bin/
bindings/**/obj/
__pycache__/
.DS_Store
```

Expected important files to commit:

```text
README.md
LICENSE
NOTICE
THIRD_PARTY_NOTICES.md
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
.github/workflows/ci.yml
include/
src/
bindings/
examples/
tests/
tools/
docs/
grammars/
vendor/
CMakeLists.txt
compila_lib.sh
```

## Verify Before Push

```bash
./compila_lib.sh
python3 -m unittest discover -s tests -v
ctest --test-dir build --output-on-failure
dotnet build examples/csharp/01_parse_string/FastParse.ParseStringExample.csproj
```

## Commit

```bash
git add .
git status --short
git commit -m "Prepare FastParse public preview"
git push origin main
```

## First Tag

After GitHub CI passes:

```bash
git tag v0.1.0-preview.10
git push origin v0.1.0-preview.10
```

The release workflow builds downloadable native packages on GitHub-hosted runners:

```text
linux-x64
macos-x64
macos-arm64
windows-x64
```

The generated archives are attached to the GitHub Release.

You can also run the release workflow manually from GitHub Actions with:

```text
workflow_dispatch
version = 0.1.0-preview.10
```
