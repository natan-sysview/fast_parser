# Java Inventory SQLite

This lab can generate a SQLite inventory for Java files under the Java Swing component collection.

Default source root:

```text
/Users/natanbarronlugo/Desktop/Proyectos/javaswing/componentes
```

Default database:

```text
data/java_swing_inventory.sqlite
```

## Generate

```bash
python3 tools/inventory_java_sqlite.py
```

Custom source root or database:

```bash
python3 tools/inventory_java_sqlite.py \
  --source-root /path/to/componentes \
  --db data/java_swing_inventory.sqlite
```

## Schema

Tables:

```text
metadata
projects
java_files
```

View:

```text
v_project_summary
```

`projects` stores one row per top-level project folder.

`java_files` stores one row per `.java` file, including:

- `project_id`
- `project_name`
- `absolute_path`
- `root_relative_path`
- `project_relative_path`
- `file_name`
- `package_name`
- `size_bytes`
- `line_count`
- `mtime_epoch`
- `sha256`

## Useful Queries

Count Java files:

```sql
SELECT COUNT(*) FROM java_files;
```

Files per project:

```sql
SELECT name, java_count, total_bytes
FROM v_project_summary;
```

Lines per project:

```sql
SELECT name, java_count, total_lines
FROM v_project_summary;
```

Get all Java paths for tests:

```sql
SELECT absolute_path
FROM java_files
ORDER BY project_name, project_relative_path;
```

## Parse Every Inventoried Java

Run TSMP against every Java file from the inventory using 12 threads:

```bash
python3 tools/parse_inventory_with_tsmp.py --workers 12
```

By default this uses the full exploration contract:

```text
format = json
rules  = all
fields = all
```

The runner discards output bytes after TSMP generates them. This keeps the benchmark focused on parse/traverse/serialize cost without writing JSON to disk.

To force Python to copy the generated output before discarding it:

```bash
python3 tools/parse_inventory_with_tsmp.py --workers 12 --copy-output
```

Run the same full AST extraction with MessagePack binary output:

```bash
python3 tools/parse_inventory_with_tsmp.py --workers 12 --format binary
```

## Persist Binary ASTs To SQLite

For integration tests that need the full AST available later without reparsing every file, use:

```bash
python3 tools/parse_inventory_binary_sqlite.py --workers 12
```

This reads file paths from:

```text
data/java_swing_inventory.sqlite
```

And writes full FastParse binary ASTs to:

```text
data/fastparse_java_ast_binary.sqlite
```

The script uses `ThreadPoolExecutor` with one `FastParse` instance per worker thread. SQLite writes are kept in the main thread and committed in batches to avoid many concurrent writers. This avoids process IPC and keeps the large binary AST payloads inside one Python process.

Output tables:

```text
parse_runs
parsed_java_files
parse_errors
```

`parsed_java_files.ast_binary` stores the full MessagePack payload returned by FastParse. The same row also stores fast metadata from the native result:

- `node_count`
- `ast_binary_bytes`
- `schema_version`
- `language`

By default the script does not scan the MessagePack nodes in Python, because that becomes the bottleneck with threads. If rule-level metadata is needed, enable:

```bash
python3 tools/parse_inventory_binary_sqlite.py \
  --workers 12 \
  --inspect-binary-metadata
```

That fills:

- `root_rule`
- `rule_counts_json`

To expand the persisted binary ASTs into one queryable row per Java AST node:

```bash
python3 tools/expand_binary_ast_nodes_sqlite.py \
  --db data/fastparse_java_ast_binary_threads_fast.sqlite \
  --run-id 1 \
  --recreate
```

This creates:

```text
ast_nodes
```

`ast_nodes` is the exploration table. It stores each grammar rule with its main fields:

- `file_name`
- `absolute_path`
- `node_id`
- `parent_id`
- `rule`
- `text`
- `text_bytes`
- `start_line`
- `start_column`
- `end_line`
- `end_column`
- `start_byte`
- `end_byte`
- `child_count`
- `children_json`

Example queries:

```sql
SELECT rule, COUNT(*)
FROM ast_nodes
GROUP BY rule
ORDER BY COUNT(*) DESC;
```

```sql
SELECT file_name, start_line, rule, text
FROM ast_nodes
WHERE rule = 'method_declaration'
ORDER BY file_name, start_line;
```

## C# AST SQLite Runner

The C# runner can build an exploration-first SQLite database directly from the inventory without first storing the binary AST BLOBs:

```bash
dotnet run --project examples/csharp/03_inventory_to_sqlite/FastParse.InventoryToSqliteExample.csproj -- \
  --workers 12 \
  --out-db data/fastparse_java_ast_nodes_csharp.sqlite
```

It uses 12 .NET threads, one `FastParseClient` per worker thread, a streaming MessagePack decoder, and one SQLite writer. The output database focuses on useful exploration tables:

```text
java_files
ast_nodes
parse_errors
```

Latest run:

```text
Files        : 1049
Errors       : 0
Nodes        : 1,649,803
Elapsed      : 9.314s
DB size      : 1.0G
```

The default contract remains the complete development contract:

```text
format = binary
rules  = all
fields = all
```

Use narrower rules or fields when the caller already knows exactly what it needs:

```bash
python3 tools/parse_inventory_binary_sqlite.py \
  --workers 12 \
  --rules "class_declaration|method_declaration" \
  --fields "id,parent_id,rule,text,byte_range"
```

Pick files for one project:

```sql
SELECT absolute_path
FROM java_files
WHERE project_name = 'java-swing-remesas-m-java17'
ORDER BY project_relative_path;
```

Find duplicate file contents:

```sql
SELECT sha256, COUNT(*) AS copies
FROM java_files
WHERE sha256 <> ''
GROUP BY sha256
HAVING copies > 1
ORDER BY copies DESC;
```
