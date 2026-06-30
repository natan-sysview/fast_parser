# Validation Workflow

This grammar keeps validation evidence under `audits/` and stable snapshots under `baselines/`.

## Full Java Inventory

Run the reusable validator:

```sh
./tools/validate_framework_inventory.py --threads 8
```

Default outputs:

- `audits/framework_inventory_validation.md`
- `audits/framework_inventory_validation.json`
- `audits/framework_inventory_validation.msgpack`

The validator:

- Reads Java file paths from the shared parser-lab inventory SQLite database.
- Preserves original bytes via SHA-256 in the report payload.
- Tries `utf-8`, then `cp1252`, then `latin-1`.
- Normalizes parser input to UTF-8 in temporary files only.
- Normalizes CRLF/CR line endings for parser input only.
- Uses worker threads.
- Deletes temporary normalized files immediately after each parse.
- Captures hard failures, `ERROR` nodes, and `MISSING` nodes.

## Private Framework Subset

Run only the framework subtype:

```sh
export FRAMEWORK_SOURCE_ROOT=/path/to/java/framework/source/root

./tools/validate_framework_inventory.py \
  --threads 8 \
  --source-root "$FRAMEWORK_SOURCE_ROOT" \
  --subtype framework \
  --json-out audits/framework_inventory_validation_private_subset.json \
  --msgpack-out audits/framework_inventory_validation_private_subset.msgpack \
  --report-out audits/framework_inventory_validation_private_subset.md
```

## Query Family Audit

Run framework capture classification:

```sh
./tools/audit_framework_queries.py
```

Default outputs:

- `audits/framework_query_family_audit.md`
- `audits/framework_query_family_audit.json`

## Cleanup Rule

Keep compact evidence and final baselines. Do not keep AST dumps, temporary normalized source copies, SQLite sidecars, or exploratory MessagePack dumps.

Quick disk check:

```sh
du -sh runs audits baselines 2>/dev/null
find . \( -name '__pycache__' -o -name '*.sqlite-wal' -o -name '*.sqlite-shm' -o -name '*.msgpack.tmp' -o -iname '*ast*' \) -print
```
