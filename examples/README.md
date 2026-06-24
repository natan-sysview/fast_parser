# FastParse Examples

Examples are runnable applications that use the public bindings.

`bindings/` contains reusable language bindings. Keep experiments, smoke apps, SQLite runners, and benchmark-style programs here in `examples/` or under `tools/`.

## Layout

```text
examples/
  python/
    01_parse_string/
    02_bulk_probe/
    03_binary_decode/
    04_inventory_to_sqlite/
    05_diagnostics_scan/

  csharp/
    01_parse_string/
    03_inventory_to_sqlite/
```

## Python

Parse a small Java source:

```bash
python3 examples/python/01_parse_string/parse_string.py --summary
```

Run a bulk probe over a directory:

```bash
python3 examples/python/02_bulk_probe/bulk_probe.py /path/to/java/root --workers 8
```

Decode binary MessagePack into Python dataclasses:

```bash
python3 examples/python/03_binary_decode/binary_decode.py
```

Read a component inventory DB, parse source files with 12 Python threads, decode
binary MessagePack into Python dataclasses, and write useful AST tables:

```bash
python3 examples/python/04_inventory_to_sqlite/inventory_to_sqlite.py \
  --inventory-db /path/to/inventario.db \
  --source-root /path/to/componentes \
  --language java \
  --extension java \
  --workers 12 \
  --out-db exports/fastparse_python_ast.sqlite
```

Run a fast parse-quality scan with diagnostics-only output:

```bash
python3 examples/python/05_diagnostics_scan/diagnostics_scan.py /path/to/java/root \
  --glob "*.java" \
  --language java \
  --workers 12 \
  --out-db exports/fastparse_python_diagnostics.sqlite
```

## C#

Parse a small Java source:

```bash
dotnet run --project examples/csharp/01_parse_string/FastParse.ParseStringExample.csproj
```

Build an exploration SQLite database from the Java inventory:

```bash
dotnet run --project examples/csharp/03_inventory_to_sqlite/FastParse.InventoryToSqliteExample.csproj -- \
  --workers 12 \
  --out-db data/fastparse_java_ast_nodes_csharp.sqlite
```
