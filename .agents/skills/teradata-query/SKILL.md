---
name: teradata-query
description: Install, configure, and use the tq CLI tool (https://github.com/remi-td/tq/) to run Teradata queries -- ad-hoc during development or as part of data product job execution.
user-invocable: true
argument-hint: [query or sql-file]
---

# Teradata Query Execution with tq

You are running Teradata queries using the **tq** CLI tool.

## What is tq?

tq is a lightweight, Rust-powered CLI client for Teradata databases. It provides one-shot queries, batch SQL file execution, and an interactive REPL -- with no Java dependencies.

Repository: https://github.com/remi-td/tq/

## Readiness Checklist

Before running any query, verify **both** prerequisites in order:

### 1. tq Installation

```bash
tq --version
```

**If missing**, follow the **tq Installation** section below.

### 2. Environment Configuration & Connection

Check if `config/environments.yaml` exists:

```bash
cat config/environments.yaml
```

**If missing**, guide the user through setup (see **Environment Setup** below).

**If present**, source the connection helper script:

```bash
source scripts/tq-connect.sh
```

This sets `TQ_LOGON` and `TQ_LOGMECH` for the session. Verify with:

```bash
tq ping
```

**If both are ready**, skip to **Running Queries**.

---

## tq Installation

Install the pre-built binary using the official installer:

```bash
export TQ_INSTALL_DIR="${PROJECT_ROOT}/scripts/tq/bin"
curl -sSL https://raw.githubusercontent.com/remi-td/tq/master/install.sh | sh -s -- --accept-license
```

The `--accept-license` flag is required for non-interactive installs (the Teradata driver is bundled and requires license acceptance).

This downloads the correct binary for your platform (macOS/Linux, Intel/ARM), verifies the checksum, and installs to `scripts/tq/bin/tq`.

Add to PATH for the session:

```bash
export PATH="${PROJECT_ROOT}/scripts/tq/bin:$PATH"
```

**Verify:**

```bash
tq --version
```

> **Note:** `scripts/tq/` is gitignored -- the binary is local to each developer's machine.

---

## Environment Setup

The project uses a dbt-style YAML config at `config/environments.yaml` to manage Teradata connection environments. This file contains credentials and is **gitignored** -- never committed.

A committed example lives at `config/environments.yaml.example`.

### Walk the user through setup:

1. **Copy the example:**

```bash
cp config/environments.yaml.example config/environments.yaml
```

2. **Ask the user for their connection details:**

> I need your Teradata connection details for the **dev** environment:
> - **Host** -- Teradata server hostname (e.g. `dev-td.company.com`)
> - **Port** -- usually `1025`
> - **Database** -- default database to connect to
> - **Username**
> - **Password**
> - **Auth mechanism** -- TD2 (default), LDAP, KRB5, or TDNEGO

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

**Always use `scripts/tq-connect.sh`** to set up the connection. Never export `TQ_LOGON` inline with each tq command -- this exposes the password in shell history and process lists.

```bash
# Connect to the default (target) environment -- do this ONCE per session
source scripts/tq-connect.sh

# Connect to a specific environment
source scripts/tq-connect.sh prod
```

The script reads `config/environments.yaml`, extracts the environment config, and exports `TQ_LOGON` and `TQ_LOGMECH`. These variables persist for the rest of the shell session -- all subsequent `tq` commands use them automatically.

**When the user requests a specific environment** (e.g. "run against prod"), re-source the script with the environment name.

**Important:** Always construct `TQ_LOGON` from `config/environments.yaml` -- never ask the user for credentials ad-hoc if the config file exists.

---

## Running Queries

### Pre-Flight: Sanitize SQL Files

Before executing any generated SQL file, run the sanitizer to replace non-ASCII characters (em dashes, smart quotes, arrows) that Teradata rejects with error 6706:

```bash
scripts/sanitize-sql.sh path/to/file.sql
```

For an entire module directory:

```bash
scripts/sanitize-sql.sh src/{product-name}/01-semantic/*.sql
```

### One-Shot Query

```bash
tq query "SELECT * FROM dbc.dbcinfo"
```

### Execute a SQL File

```bash
tq query --file src/{product-name}/01-semantic/01-data_product_map.sql
```

### Execute Multiple SQL Files (deployment)

Use the deployment script for automated phased execution:

```bash
scripts/deploy.sh {product-name}
```

Or run files manually in order:

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

Use the deployment script for automated phased execution:

```bash
scripts/deploy.sh {product-name}
```

Or execute generated SQL files manually in module deployment order:

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
- For batch file execution, stop on first error -- do not continue executing subsequent files.
- Always review error output before retrying. Common issues:
  - **3807** -- Object does not exist (check database/table name)
  - **3706** -- Syntax error (validate SQL with the teradata-sql prompt first)
  - **2801** -- Authentication failed (check environment config in `config/environments.yaml`)
  - **6706** -- Untranslatable character (run `scripts/sanitize-sql.sh` on the SQL file)

## Key Rules

- **Never hardcode credentials** in SQL files, scripts, or committed configuration.
- **Always use `config/environments.yaml`** as the single source for connection details -- never ask for credentials ad-hoc if the config file exists.
- **Always use `source scripts/tq-connect.sh`** to set connection variables once per session -- never export `TQ_LOGON` inline with each tq command.
- **Always sanitize SQL files** with `scripts/sanitize-sql.sh` before execution to strip non-ASCII characters.
- **Always use `--file`** for executing generated SQL rather than pasting long statements inline.
- **Follow deployment order** -- Memory + Semantic first, then Domain + Observability, then Search + Prediction.
- **Validate SQL** with the **teradata-sql** prompt before executing DDL against production.
- **Confirm environment** before executing against non-dev targets -- always ask the user before running against uat or prod.
