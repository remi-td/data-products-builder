---
name: teradata-source-image
description: Compile and deploy Teradata Source Image patterns (SCD Type 2 history loads). Use when the user wants to set up a history-tracking (SCD Type 2) or append-only staging target table in Teradata Vantage.
user-invocable: true
argument-hint: [target table or config file path]
---

# Teradata Source Image — Staging and Historization Pattern

You help the user build, compile, and deploy the **Source Image** staging pattern on Teradata Vantage. This pattern supports building a persistent "gold" copy of source entities with full temporal history management (SCD Type 2), separating the logical schema definitions from physical loading mechanisms.

## When to use

- "Set up a history table for our customer staging source."
- "Load this staging data into a target table while tracking history (SCD Type 2)."
- "Configure a temporal history load in Teradata."
- "Write SQL to compact and historize changes from a delta batch."

## Agent Quickstart Checklist

Run through this before generating any files:

1. **Identify Staging Source & Target Schemas**: Get the names of the source staging table, the target table, primary key columns, value/tracked columns, and the time-change column (representing transaction/change time).
2. **Determine Temporal Mode**:
   - **Open-Ended (`use_valid_to = N`)**: The source staging table only has a `valid_from` or `last_update` timestamp. History records remain open-ended until a new change is imported.
   - **Closed-Ended (`use_valid_to = Y`)**: The source staging table provides both `valid_from` and `valid_to` timestamps.
3. **Compile the SQL Script**: Use the local compiler tool `compile_source_image.py` to generate the complete, optimized SQL script.
4. **Execute using `teradata-query`**: Deploy the compiled SQL using the `teradata-query` skill (leveraging `tq`).

## How to Compile

Run the Python-based compiler to generate the SQL script. You can pass configuration either via command-line arguments or using a JSON configuration file.

### Option A: Using a JSON configuration file (Recommended)

1. Create a configuration file, e.g. `customer_config.json`:
   ```json
   {
     "source_table": "stg_customers",
     "target_table": "sim_customers",
     "key_columns": "customer_id",
     "time_change_column": "last_update_ts",
     "tracked_columns": "first_name,last_name,email",
     "use_valid_to": false,
     "valid_period_column": "valid_period",
     "columns_with_types": {
       "customer_id": "INTEGER",
       "first_name": "VARCHAR(100)",
       "last_name": "VARCHAR(100)",
       "email": "VARCHAR(255)"
     }
   }
   ```

2. Compile the template:
   ```bash
   python3 scripts/compile_source_image.py --config customer_config.json --output customer_load.sql
   ```

### Option B: Using command-line flags directly

```bash
python3 scripts/compile_source_image.py \
  --source-table stg_customers \
  --target-table sim_customers \
  --key-columns customer_id \
  --time-change-column last_update_ts \
  --tracked-columns first_name,last_name,email \
  --columns-with-types "customer_id:INTEGER,first_name:VARCHAR(100),last_name:VARCHAR(100),email:VARCHAR(255)" \
  --valid-period-column valid_period \
  --output customer_load.sql
```

## How to Execute (via `teradata-query` / `tq`)

Once the SQL script is generated, execute it against your Teradata instance using the existing `teradata-query` (tq) tool:

```bash
tq run -f customer_load.sql
```

Refer to the [teradata-query](https://github.com/remi-td/tq/tree/master/agentic/skills/teradata-query) skill for setting up connection profiles and executing raw queries.

## Batched-Autocommit Loader (Prefer over FastLoad on Flaky Connections)

On environments where connections may drop mid-flight (trial instances, VPN tunnels, bandwidth-limited networks), prefer the **batched-autocommit INSERT** pattern over FastLoad:

| Concern | FastLoad (`{fn teradata_try_fastload}`) | Batched-Autocommit INSERT |
|---------|----------------------------------------|--------------------------|
| Mid-flight kill | Orphans table lock (Error 2652) | Commits every N rows — safe to interrupt |
| Resumability | None — must DROP+recreate table | `SELECT COUNT(*)` from target, skip that many source rows |
| Throughput | Higher (ML protocol) | Lower but acceptable for ≤ 1 MB/s wire |
| FastLoad slot requirement | Yes | None |

When using the batched-autocommit pattern, always:
1. Open one connection **per entity** (not shared across entities)
2. Set `autocommit = True` — each `executemany` batch is its own committed transaction
3. On restart, `SELECT COUNT(*)` from the target table, then skip that many leading rows from the source file

Reference implementation: `workspace/src/{product-name}/scripts/load_staging_resume.py`

## Column Count Derivation — Always Read the File Header

Never assume column counts from codebooks, data dictionaries, or architect briefs. Column counts must always be derived from the **actual source file header**:

```python
with open(tsv_path, encoding="latin-1") as fh:
    header = fh.readline().rstrip("\r\n").split("\t")
ncols = len(header)
```

Codebook counts frequently reflect a schema version that differs from the actual extract. For example, in one data product build, the brief stated 268/269 columns for certain staging tables; the actual TSV headers showed 363/381. DDL generated from the wrong count fails on INSERT-SELECT with a column mismatch error.

**Important:** Do not use shell tools (`wc -l`, `head -N`, `awk`, `cut`) on large TSV files when the RTK shell proxy is active — it corrupts multi-line output. Use Python for all header inspection and row counting on data files.

## Hard Rules

- **Use Volatile SET Staging Tables**: Deduping and overlap computations must be performed in volatile staging tables (`hist_prep_1`, `hist_prep_2`, `hist_prep_3`) to ensure high-performance transaction boundaries without writing to permanent table logs.
- **Normalize Meet Compaction**: Always use `TD_SYSFNLIB.TD_NORMALIZE_MEET` with `HASH BY` and `LOCAL ORDER BY` on the primary key columns to distribute compaction across AMPs.
- **Explicit Column Inserts**: Never use `INSERT INTO ... SELECT *` for permanent tables or volatile tables populated by unions. Explicitly specify the column names in both the target definition and select statements to avoid order mismatches.
