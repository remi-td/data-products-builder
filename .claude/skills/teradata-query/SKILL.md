---
name: teradata-query
description: Install, configure, and use the tq CLI tool (https://github.com/remi-td/tq/) to run Teradata queries — ad-hoc during development or as part of data product job execution.
user-invocable: true
argument-hint: [query or sql-file]
---

# Teradata Query Execution with tq

You are running Teradata queries using the **tq** CLI tool.

## What is tq?

tq is a lightweight, Rust-powered CLI client for Teradata databases. It provides one-shot queries, batch SQL file execution, and an interactive REPL — with no Java dependencies.

Repository: https://github.com/remi-td/tq/

## Readiness Checklist

Before running any query, verify **both** prerequisites in order:

### 1. Environment Configuration

Check if `config/environments.yaml` exists:

```bash
cat config/environments.yaml
```

**If missing**, guide the user through setup (see **Environment Setup** below).

**If present**, parse it to determine the active environment (the `target` key) and build the `TQ_LOGON` string.

### 2. tq Installation

```bash
tq --version
```

**If missing**, follow the **tq Installation** section below.

**If both are ready**, skip to **Running Queries**.

---

## Environment Setup

The project uses a dbt-style YAML config at `config/environments.yaml` to manage Teradata connection environments. This file contains credentials and is **gitignored** — never committed.

A committed example lives at `config/environments.yaml.example`.

### Walk the user through setup:

1. **Copy the example:**

```bash
cp config/environments.yaml.example config/environments.yaml
```

2. **Ask the user for their connection details:**

> I need your Teradata connection details for the **dev** environment:
> - **Host** — Teradata server hostname (e.g. `dev-td.company.com`)
> - **Port** — usually `1025`
> - **Database** — default database to connect to
> - **Username**
> - **Password**
> - **Auth mechanism** — TD2 (default), LDAP, KRB5, or TDNEGO

3. **Write the file** with the provided values. Always include at least a `dev` environment and set `target: dev`.

4. **Confirm** the file is gitignored:

```bash
git check-ignore config/environments.yaml
```

### File Format

```yaml
# config/environments.yaml
target: dev

environments:
  dev:
    host: dev-td.company.com
    port: 1025
    database: dev_sandbox
    user: my_user
    password: my_password
    logmech: TD2

  uat:
    host: uat-td.company.com
    port: 1025
    database: uat_db
    user: my_user
    password: my_password
    logmech: TD2

  prod:
    host: prod-td.company.com
    port: 1025
    database: prod_db
    user: my_user
    password: my_password
    logmech: LDAP
```

### Switching Environments

To change the active environment, update the `target` key:

```yaml
target: uat   # now all queries go to UAT
```

Or the user can request a specific environment when invoking queries: "run this against prod".

---

## Connecting tq to an Environment

Read `config/environments.yaml`, extract the environment matching the `target` key, and export the `TQ_LOGON` environment variable before running tq:

```bash
export TQ_LOGON="{user}:{password}@{host}:{port}/{database}"
export TQ_LOGMECH="{logmech}"
```

For example, given the dev environment above:

```bash
export TQ_LOGON="my_user:my_password@dev-td.company.com:1025/dev_sandbox"
export TQ_LOGMECH="TD2"
```

**When the user requests a specific environment** (e.g. "run against prod"), use that environment's config instead of the `target` default.

**Important:** Always construct `TQ_LOGON` from `config/environments.yaml` — never ask the user for credentials ad-hoc if the config file exists.

---

## tq Installation

tq requires the Rust toolchain. Install it if not present:

```bash
# Install Rust (if not already available)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
```

Then install tq from source into the project's `scripts/` directory:

```bash
# Clone and build tq
cd /tmp
git clone https://github.com/remi-td/tq.git
cd tq
cargo install --path . --root "${PROJECT_ROOT}/scripts/tq"
```

After installation, the binary is at `scripts/tq/bin/tq`. Add it to PATH or invoke it directly.

**Verify:**

```bash
scripts/tq/bin/tq --version
```

> **Note:** `scripts/tq/` is gitignored — the binary is local to each developer's machine.

---

## Running Queries

### One-Shot Query

```bash
tq query "SELECT * FROM dbc.dbcinfo"
```

### Execute a SQL File

```bash
tq query --file src/{product-name}/01-semantic/01-data_product_map.sql
```

### Execute Multiple SQL Files (deployment)

Run files in order during data product deployment:

```bash
for f in src/{product-name}/01-semantic/*.sql; do
  echo "--- Executing: $f ---"
  tq query --file "$f"
done
```

### Batch Statements from Stdin

```bash
tq query <<'EOF'
SELECT CURRENT_DATE;
SELECT DATABASE;
EOF
```

### Export Results

```bash
# CSV
tq query "SELECT * FROM sales_summary" --format csv > report.csv

# JSON
tq query "SELECT * FROM products" --format json > products.json
```

### Interactive REPL

For exploratory work:

```bash
tq repl
```

Useful REPL metacommands:

| Command | Purpose |
|---------|---------|
| `/list databases` | List all databases |
| `/list tables pattern%` | List tables matching pattern |
| `/describe table_name` | Show table structure |
| `/sample table_name 20` | Random sample (20 rows) |
| `/peek table_name` | Preview structure + data |
| `/sessions` | Monitor active sessions |

### Connection Check

```bash
tq ping
```

---

## Usage Patterns in the Build Process

### During Design (ad-hoc validation)

Use tq to verify existing structures or test assumptions:

```bash
# Check if a database/table already exists
tq query "SELECT * FROM dbc.tablesV WHERE DatabaseName = 'MyProduct_Domain'"

# Inspect existing table DDL
tq query "SHOW TABLE MyProduct_Domain.Party_H"
```

### During Deployment (execute DDL/DML)

Execute generated SQL files in module deployment order:

```bash
# Phase 1: Memory + Semantic
tq query --file src/{product}/01-memory/01-tables.sql
tq query --file src/{product}/01-semantic/01-tables.sql
tq query --file src/{product}/01-semantic/02-seed-data.sql

# Phase 2: Domain + Observability
tq query --file src/{product}/02-domain/01-tables.sql
tq query --file src/{product}/02-domain/02-views.sql

# Phase 3: Search + Prediction
tq query --file src/{product}/03-search/01-tables.sql
tq query --file src/{product}/03-prediction/01-tables.sql
```

### During Validation (post-deployment checks)

```bash
# Verify Semantic module registration
tq query "SELECT * FROM {Product}_Semantic.data_product_map"

# Verify entity metadata
tq query "SELECT * FROM {Product}_Semantic.entity_metadata ORDER BY module_name"

# Test a current-state view
tq query "SELECT TOP 10 * FROM {Product}_Domain.Party_Current"
```

---

## Error Handling

- If a query fails, tq prints the Teradata error code and message to stderr.
- For batch file execution, stop on first error — do not continue executing subsequent files.
- Always review error output before retrying. Common issues:
  - **3807** — Object does not exist (check database/table name)
  - **3706** — Syntax error (validate SQL with the teradata-sql skill first)
  - **2801** — Authentication failed (check environment config in `config/environments.yaml`)

## Key Rules

- **Never hardcode credentials** in SQL files, scripts, or committed configuration.
- **Always use `config/environments.yaml`** as the single source for connection details — never ask for credentials ad-hoc if the file exists.
- **Always use `--file`** for executing generated SQL rather than pasting long statements inline.
- **Follow deployment order** — Memory + Semantic first, then Domain + Observability, then Search + Prediction.
- **Validate SQL** with the **teradata-sql** skill before executing DDL against production.
- **Confirm environment** before executing against non-dev targets — always ask the user before running against uat or prod.
