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

Try connection sources **in priority order**:

#### Option A: `config/environments.yaml` (preferred for project work)

```bash
cat config/environments.yaml
```

**If present**, source the connection helper script:

```bash
source scripts/tq-connect.sh
```

This sets `TQ_LOGON` and `TQ_LOGMECH` for the session.

#### Option B: User-provided connection string or environment variable

If `config/environments.yaml` does not exist, the user may provide connection details via an environment variable, a direct string, or other means. Convert whatever they provide to `TQ_LOGON` format (`user:pass@host:port/db`):

```bash
# If the user provides a URI with a scheme prefix (e.g. teradata://user:pass@host:port/db):
export TQ_LOGON="${USER_PROVIDED_VAR#teradata://}"

# If the user provides a plain connection string:
export TQ_LOGON="user:pass@host:port/db"
```

> **Important:** Do NOT use pipes (e.g. `echo "$VAR" | sed ...`) to set TQ_LOGON — the pipe leaves stdin in a piped state that conflicts with tq's query argument detection (see **Stdin Conflict** below). Use shell parameter expansion instead.

#### Option C: No connection details available

Guide the user through setup (see **Environment Setup** below).

#### Verify connectivity

Whichever option was used, confirm with `tq ping` — this is a **database-level** connectivity test (connects to Teradata, executes a query, reports latency), not a network ping:

```bash
tq ping
```

You can also pass credentials directly via `-l`/`--logon` without setting environment variables — useful for quick one-off checks:

```bash
tq -l "user:pass@host:port/db" ping
```

**If ready**, skip to **Running Queries**.

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

## Stdin Conflict: Use `--file` in Automated Environments

**Critical:** When running tq from automation tools, CI pipelines, or AI agent harnesses (e.g. Claude Code's Bash tool), stdin is often in a piped state. tq detects this as a second input source and rejects the command with:

```
Error: Invalid configuration: Multiple input sources provided: query argument, piped stdin.
```

**Workaround:** Always use `--file` instead of positional query arguments:

```bash
# WRONG in automated environments:
tq query "SELECT 1"

# CORRECT — write SQL to a temp file first:
echo "SELECT 1" > /tmp/q.sql && tq query --file /tmp/q.sql

# CORRECT — for multi-statement or complex queries:
cat > /tmp/q.sql <<'EOSQL'
SELECT DatabaseName FROM DBC.DatabasesV
WHERE DatabaseName LIKE 'MyProduct%'
ORDER BY DatabaseName
EOSQL
tq query --file /tmp/q.sql
```

**When does this NOT apply?** Interactive terminal sessions (e.g. the user running tq directly) work fine with positional arguments. The conflict only occurs when stdin is piped by the parent process.

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

### Connection Failures

If `tq ping` or any `tq` command fails with a connection error, **always validate the connection string format before assuming a network issue**:

1. **Check for scheme prefixes:** `TQ_LOGON` must be `user:pass@host:port/db` — no `teradata://`, `jdbc:`, or other URI scheme prefix. If the source variable (e.g. `$DATABASE_URI`) contains a scheme, strip it:
   ```bash
   export TQ_LOGON="${DATABASE_URI#teradata://}"
   ```

2. **Check the string structure:** It must match `user:password@host:port/database`. Common issues:
   - Missing port (default is `1025`)
   - Extra path segments or query parameters from JDBC/URI formats
   - URL-encoded characters that tq doesn't decode (e.g. `%40` instead of `@`)

3. **Inspect the actual value** (mask the password) to verify format:
   ```bash
   echo "$TQ_LOGON" | sed 's/:[^:@]*@/:***@/'
   ```

4. **Only after confirming the string is well-formed**, investigate network issues (host reachability, firewall, VPN, environment not running).

### Query Errors

- If a query fails, tq prints the Teradata error code and message to stderr.
- For batch file execution, stop on first error -- do not continue executing subsequent files.
- Always review error output before retrying. Common issues:
  - **3807** -- Object does not exist (check database/table name)
  - **3706** -- Syntax error (validate SQL with the teradata-sql prompt first)
  - **2801** -- Authentication failed (check environment config in `config/environments.yaml`)
  - **6706** -- Untranslatable character (run `scripts/sanitize-sql.sh` on the SQL file)

## Key Rules

- **Never hardcode credentials** in SQL files, scripts, or committed configuration.
- **Use `config/environments.yaml`** as the primary source for connection details. If it doesn't exist, use whatever connection info the user provides. Never ask for credentials ad-hoc if a source already exists.
- **Set `TQ_LOGON` once per session** -- via `source scripts/tq-connect.sh` (Option A) or by converting user-provided credentials (Option B). Never export `TQ_LOGON` inline with each tq command. Avoid pipes when setting TQ_LOGON -- use shell parameter expansion.
- **Always sanitize SQL files** with `scripts/sanitize-sql.sh` before execution to strip non-ASCII characters.
- **Always use `--file`** for executing generated SQL rather than pasting long statements inline.
- **Follow deployment order** -- Memory + Semantic first, then Domain + Observability, then Search + Prediction.
- **Validate SQL** with the **teradata-sql** prompt before executing DDL against production.
- **Confirm environment** before executing against non-dev targets -- always ask the user before running against uat or prod.
