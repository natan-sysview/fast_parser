# Contributing

Thanks for contributing to FastParse.

## Project Boundaries

Keep these folders conceptually separate:

```text
bindings/  reusable language bindings
examples/  runnable example applications
tools/     internal maintenance, inventory, and benchmark scripts
src/       native C core
include/   public C headers
docs/      public contracts and design notes
```

Do not put experiments, smoke apps, or SQLite lab runners inside `bindings/`.

## Native Core Rules

The C core must remain memory-only.

Do not add:

- File reading.
- File writing.
- Directory walking.
- Database creation.
- Application-level logging.
- Thread pool management.

The parent language/application owns those responsibilities.

## Public API Rules

Prefer public names:

```text
fastparse_version
fastparse_parse
fastparse_result_free
```

The `tsmp_*` names are compatibility aliases.

When changing public behavior, update:

- `include/fastparse.h`
- `include/tsmp.h`
- `docs/contracts.md`
- `docs/c_api.md`
- `docs/binary_schema.md` when binary output changes
- Bindings and examples

## Tests

Before opening a pull request:

```bash
./compila_lib.sh
python3 -m unittest discover -s tests -v
ctest --test-dir build --output-on-failure
dotnet build examples/csharp/01_parse_string/FastParse.ParseStringExample.csproj
```

## Generated Files

Do not commit:

```text
build/
bin/
data/*.sqlite
*.sqlite-shm
*.sqlite-wal
examples/**/bin/
examples/**/obj/
bindings/**/bin/
bindings/**/obj/
__pycache__/
.DS_Store
```

## Documentation

New features should include documentation useful to both humans and coding agents.

Prefer concrete examples over abstract descriptions.
