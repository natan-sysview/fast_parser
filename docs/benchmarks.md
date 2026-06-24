# Benchmarks

Benchmarks are run against the SQLite Java inventory:

```text
data/java_swing_inventory.sqlite
```

Current corpus:

```text
Java files : 1049
Lines      : 400,007
Source     : 13,384,187 bytes
Library    : fastparse-c-api/0.5.0
Platform   : macOS arm64
```

## Run

```bash
python3 tools/benchmark_tsmp_formats.py \
  --workers 1,4,8,12 \
  --out data/tsmp_benchmark_results.json
```

The benchmark uses `parse_bytes_summary`, so TSMP still generates the native output but Python does not copy the full payload unless a scenario enables `copy_output`.

## Scenarios

| Scenario | Format | Rules | Fields |
|---|---|---|---|
| `stats_all` | stats | all | all |
| `json_all` | json | all | all |
| `binary_all` | binary | all | all |
| `json_structural` | json | all | `id,parent_id,rule,range,byte_range` |
| `binary_structural` | binary | all | `id,parent_id,rule,range,byte_range` |
| `csv_declarations` | csv | declarations only | `id,parent_id,rule,range,byte_range` |

Declarations are:

```text
class_declaration
interface_declaration
enum_declaration
method_declaration
constructor_declaration
```

## Current Results

Results below are from 12 workers.

| Scenario | Time | Output | Nodes | Errors |
|---|---:|---:|---:|---:|
| `stats_all` | 0.186s | 0 bytes | 1,649,803 | 0 |
| `json_all` | 1.961s | 654,993,616 bytes | 1,649,803 | 0 |
| `binary_all` | 0.319s | 543,047,149 bytes | 1,649,803 | 0 |
| `json_structural` | 1.479s | 241,533,869 bytes | 1,649,803 | 0 |
| `binary_structural` | 0.257s | 181,641,868 bytes | 1,649,803 | 0 |
| `csv_declarations` | 0.196s | 1,123,685 bytes | 21,250 | 0 |

## Observations

Binary MessagePack is the preferred high-performance interchange format.

For full AST exploration:

```text
JSON all   : 1.961s, 654.99 MB
BINARY all : 0.319s, 543.05 MB
```

For structural indexing without `text`:

```text
JSON structural   : 1.479s, 241.53 MB
BINARY structural : 0.257s, 181.64 MB
```

`stats_all` remains the parse/traverse baseline because it does not serialize output.
