# Teradata ETL MCP Extension

Use GitHub Copilot to build and run ELT/ETL pipelines across Teradata, Airflow, Airbyte, and dbt — all in plain English from VS Code.

> **📦 Install as VS Code Extension:**  
> Install from VSIX: Extensions panel → `...` → **Install from VSIX...** → select `elt-mcp-server-*.vsix`  
> Or via CLI: `code --install-extension elt-mcp-server-*.vsix` · Requires **VS Code 1.100+**

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Installing the Extension](#installing-the-extension)
  - [Extension Commands](#extension-commands)
  - [SSH Setup (Bidirectional)](#ssh-setup-bidirectional)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables-env)
  - [Connection Profiles](#connection-profiles)
    - [Setup via Wizard](#setup-via-wizard)
    - [File Format](#file-format)
    - [Getting a Profile Template](#getting-a-profile-template)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [Example Prompts](#example-prompts)
- [Acknowledgments](#acknowledgments)

---

## Features

| Capability | What you can do |
|------------|----------------|
| **Teradata** | Query tables, export data to CSV, profile schemas, compare structures |
| **Airflow** | Deploy DAGs, trigger runs, monitor status, manage schedules and connections |
| **Airbyte** | Create sources & destinations, browse connectors, select streams, trigger syncs |
| **dbt** | Scaffold projects, generate staging & mart models, run tests, view dependency graphs |
| **CSV Loading** | Import CSV files directly into Teradata tables with automatic schema detection |
| **TdLoad / TPT** | Enterprise-grade parallel loading into Teradata; generate Airflow DAGs to automate loading pipelines |
| **Connection Profiles** | Manage named credential profiles — passwords never exposed to the AI |

### Security: Credential Isolation

The AI **never** sees your passwords, tokens, or API keys. All credentials are stored in `connections.yaml` and resolved server-side. You only tell the AI which **profile name** to use:

```
You:  "Export customers from profile teradata_prod to CSV"
  ↓
Copilot references profile name "teradata_prod" — no password ever sent to the AI
  ↓
MCP Server resolves credentials from connections.yaml and connects to Teradata
  ↓
Result returned — success/failure only, no secrets in the response
```

---

## Architecture

The extension runs as a local MCP server inside VS Code, translating Copilot instructions into actions across your data systems:

```
+---------------------------------------------------------------+
|                       MCP Server Layer                         |
|  +----------------------------------------------------------+ |
|  |  22 Tools across 7 Categories                              | |
|  +----------------------------------------------------------+ |
+---------------------------------------------------------------+
                              |
+---------------------------------------------------------------+
|                   Pipeline Orchestrator                        |
|  +-------------------+ +------------------+ +--------------+ |
|  | Credential        | | Code Generators  | | Workflow     | |
|  | Resolver          | | (DAG, dbt,       | | Orchestrator | |
|  | (connections.yaml)| |  TdLoad)         | | (Airflow)    | |
|  +-------------------+ +------------------+ +--------------+ |
|  +-----------------+ +------------------+ +--------------+   |
|  | Response        | | Audit Logger     | | Metadata     |   |
|  | Sanitizer       | | & Reliability    | | Store        |   |
|  +-----------------+ +------------------+ +--------------+   |
+---------------------------------------------------------------+
                              |
+---------------------------------------------------------------+
|                        Client Layer                            |
|  +----------+ +----------+ +----------+ +-----+ +-------+    |
|  | Teradata | | Airflow  | | Airbyte  | | dbt | |  TTU  |    |
|  | Client   | | Client   | | Client   | |     | | Client|    |
|  +----------+ +----------+ +----------+ +-----+ +-------+    |
+---------------------------------------------------------------+
                              |
+---------------------------------------------------------------+
|                      External Systems                          |
|  +----------+ +----------+ +----------+ +-----+ +-------+    |
|  | Teradata | | Airflow  | | Airbyte  | | dbt | |  TTU  |    |
|  | Database | | Server   | | Server   | | Proj| | Tools |    |
|  +----------+ +----------+ +----------+ +-----+ +-------+    |
+---------------------------------------------------------------+
```

---

## Installation

### Prerequisites

| Requirement | When needed |
|-------------|-------------|
| **VS Code 1.100+** | Always |
| **Python 3.10+** | Always (install manually; the extension creates a virtual environment and installs dependencies automatically) |
| **GitHub Copilot Chat extension** | Always |
| **Teradata Tools & Utilities (TTU) 17.20+** | Optional — only needed for CSV → Teradata and Teradata → CSV data loading |
| ↳ **`tdload`** (TdLoad) | Included in TTU — used for high-speed CSV/table loads into Teradata |
| **Apache Airflow 2.x** | Optional — only needed for DAG orchestration |
| **Airbyte OSS** | Optional — only needed for data replication |

> **TTU Download**: Get Teradata Tools & Utilities from [Teradata Downloads](https://downloads.teradata.com/). Install with at least the **TdLoad** component selected. After install, verify with `tdload --version`.

---

### Installing the Extension

Install the VS Code extension from a `.vsix` file:

**Option 1 — VS Code UI:**

1. Open VS Code
2. Press `Ctrl+Shift+X` → click the `...` (More Actions) menu → **Install from VSIX...**
3. Select the `.vsix` file (`elt-mcp-server-*.vsix`)
4. Click **Reload** when prompted

**Option 2 — Command line:**

```bash
code --install-extension elt-mcp-server-*.vsix
```

**After installation:**

The **Setup Wizard** opens automatically on first install. Fill in your details and click **Save & Continue** — the extension starts the MCP server automatically.

If you close the wizard and need to reopen it later:

1. Open Command Palette (`Ctrl+Shift+P`)
2. Run **Teradata ETL MCP Extension: Setup Wizard**

> The extension creates and manages a Python virtual environment automatically. No manual `pip install` is needed.
> - **Windows**: `%APPDATA%\Code\User\globalStorage\teradata.elt-mcp-server\venv`
> - **macOS/Linux**: `~/.vscode/extensions/teradata.elt-mcp-server-*/venv`

### Extension Commands

| Command | Description |
|---------|-------------|
| `Teradata ETL MCP Extension: Setup Wizard` | Open the configuration wizard |
| `Teradata ETL MCP Extension: Validate Connections` | Test all configured connections |
| `Teradata ETL MCP Extension: Reload Configuration` | Restart the MCP server with updated config |
| `Teradata ETL MCP Extension: Show Setup Logs` | Open the extension output channel |
| `Teradata ETL MCP Extension: Recreate Python Environment` | Delete and rebuild the managed venv |
| `Teradata ETL MCP Extension: Clear All Configuration` | Reset all stored settings |

### SSH Setup (Bidirectional)

> **Only required if you use Airflow for DAG deployment.** If you are only using Teradata, Airbyte, or dbt, you can skip this section.

The system requires **bidirectional SSH** between the MCP client machine and the Airflow server:

| Direction | Purpose | When Needed |
|-----------|---------|-------------|
| MCP Client → Airflow Server | Deploy generated DAG files via SFTP | Required for DAG deployment |
| Airflow Server → MCP Client | Execute TdLoad/TPT commands remotely via SSH | When using TdLoad or TPT operators |

```
MCP Client Machine                          Airflow Server (Linux)
+---------------------+                    +---------------------+
| - MCP Server        | --- SSH/SFTP ----> | - /opt/airflow/dags |
| - TTU (tpt,         |   DAG deployment   | - Airflow Scheduler |
|   tdload)           |                    | - Airflow Workers   |
| - SSH Server        | <--- SSH --------- |                     |
|   (for runtime)     |  TdLoad exec       |                     |
+---------------------+                    +---------------------+
```

For full step-by-step instructions — see **[SSH-SETUP.md](SSH-SETUP.md)**.

---

## Configuration

Two configuration files control the extension's behaviour:

- **`.env`** — SSH connection settings and TTU binary paths. The Setup Wizard configures these for you when you fill in the Airflow and TTU sections.
- **`connections.yaml`** — Named credential profiles for Teradata, Postgres, Airbyte, and other systems. You create this file yourself (see [File Format](#file-format) below) and upload it via the Setup Wizard → **Advanced** section.

### Environment Variables (`.env`)

> **Wizard-managed settings** — Teradata, Airflow API, and Airbyte credentials are configured directly in the wizard and stored securely. Do **not** put them in `.env`.

| Section | Variable | Description | Required? |
|---------|----------|-------------|-----------|
| **Airflow DAG Deployment** | `AIRFLOW_REMOTE_HOST` | Airflow server hostname for SSH DAG deployment | For DAG deployment |
| | `AIRFLOW_REMOTE_USER` | SSH username on the Airflow server | For DAG deployment |
| | `AIRFLOW_REMOTE_SSH_KEY` | Path to SSH private key (on this machine) | For DAG deployment |
| | `AIRFLOW_REMOTE_PASSWORD` | SSH password (if not using key auth) | No |
| | `AIRFLOW_REMOTE_PORT` | SSH port on Airflow server | No (default: `22`) |
| | `AIRFLOW_REMOTE_SSH_KEY_PASSPHRASE` | Passphrase for the SSH key | No |
| | `AIRFLOW_DAG_FOLDER` | Remote DAG folder path on the Airflow server | No (default: `/opt/airflow/dags`) |
| **MCP Client SSH** *(only needed when Airflow runs TdLoad/TPT remotely)* | `MCP_CLIENT_SSH_HOST` | This machine's hostname/IP (Airflow SSHes back here at runtime) | For runtime SSH |
| | `MCP_CLIENT_SSH_USER` | SSH username on this machine | For runtime SSH |
| | `MCP_CLIENT_SSH_PORT` | SSH port on this machine | No (default: `22`) |
| | `MCP_CLIENT_SSH_KEY_PATH` | Path to SSH private key **on the Airflow worker** | For runtime SSH |
| | `MCP_CLIENT_SSH_PASSWORD` | SSH password on this machine (if not using key auth) | No |
| **MCP Server** | `MCP_LOG_LEVEL` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | No (default: `INFO`) |
| | `MCP_LOG_FILE` | Log file path | No |
| | `MCP_FAIL_FAST_ON_STARTUP` | Stop server startup if a connection check fails at launch | No (default: `false`) |
| | `MCP_REDIS_URL` | Redis URL for distributed state (advanced, optional) | No |
| **TTU** | `TTU_ENABLED` | Enable local TPT/TdLoad execution | No (default: `false`) |
| | `TTU_TTU_VERSION` | TTU version (e.g., `17.20`); auto-detected if not set | No |
| | `TTU_TPT_BINARY_PATH` | Path to `tbuild` binary (auto-detected from version) | No |
| | `TTU_TDLOAD_BINARY_PATH` | Path to `tdload` binary (auto-detected from version) | No |
| | `TTU_COMMAND_TIMEOUT` | Subprocess timeout in seconds | No (default: `600`) |

---

### Connection Profiles

Connection profiles store named credentials for Teradata, Postgres, and other systems. The AI references profiles by **name only** — passwords and keys are never exposed.

#### Setup via Wizard

Create your `connections.yaml` file and upload it through the Setup Wizard → **Advanced** section:

1. Open Command Palette → **Teradata ETL MCP Extension: Setup Wizard**
2. Go to the **Advanced** section
3. Upload your `connections.yaml` file

#### File Format

```yaml
version: "1"

profiles:
  postgres_prod:
    host: "pg-host.example.com"
    port: 5432
    database: "testdb"
    username: "testuser"
    password: "${POSTGRES_PASSWORD}"   # env var interpolation
    schemas:
      - "public"
    description: "Production Postgres database"

  teradata_prod:
    host: "td-host.example.com"
    port: 1025
    username: "dbc"
    password: "${TERADATA_PASSWORD}"
    default_schema: "analytics_raw"
    description: "Production Teradata destination"

aliases:
  source: "postgres_prod"
  teradata: "teradata_prod"
```

> **Tips:**
> - `${ENV_VAR}` values are resolved from OS environment variables (set them in your shell or via a `.env` file)
> - `description` is the only field visible to the AI — all credentials are hidden
> - Aliases let you use short names (e.g. `source` instead of `postgres_prod`)
> - After editing `connections.yaml`, ask Copilot: *"Reload connection profiles"* — no server restart needed

#### Getting a Profile Template

Not sure what fields a connector needs? Ask Copilot — it returns the required fields for that connector type as a ready-to-paste `connections.yaml` block:

```
Provide me the connection profile template for Postgres
```

```
Provide me the connection profile template for Teradata
```

```
Provide me the connection profile template for MySQL
```

The response includes all required, optional, and secret fields clearly marked — fill in your values and paste into `connections.yaml`.

---

## Usage

### Starting the Server

The MCP server starts automatically when VS Code loads. If you need to manually start or restart it:

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Run **MCP: List Servers**
3. Select **Teradata ETL MCP Extension**
4. Click **Start Server**

### Example Prompts

The examples below show natural-language prompts you can type directly in GitHub Copilot Chat. Copilot handles the rest automatically.

---

#### 🗄️ Teradata — Export & Explore

```
Export demo_db.customers from profile teradata_prod to customers_export.csv
```

```
List all tables in the test database using profile teradata_prod
```

```
Profile the test.customers table — show row count, column types, and null rates
```

---

#### 🔧 dbt — Project & Model Generation

```
Scaffold a new dbt sub-project named customers_analytics, bound to the wizard Teradata profile
```

```
Generate staging models for test.customers and test.products bound to the wizard Teradata profile
```

```
Create staging models for all remaining tables in the test schema using the wizard Teradata profile
(tables: sales_orders, order_items)
```

```
Analyze the staging views in customers_analytics and create mart models for analytics using the wizard Teradata profile
```

```
Run all dbt tests in customers_analytics and show me the model dependency graph
```

---

#### 🔌 Airbyte — Sources, Destinations & Connections

```
List all available connector types in Airbyte
```

```
Create an Airbyte source for Postgres using connection profile postgres_prod
```

```
Create an Airbyte destination for Teradata using connection profile airbyte_teradata_profile
```

```
List all available streams from the Postgres source I just created
```

```
Create an Airbyte connection to transfer the customers stream from the Postgres source to the Teradata destination
```

---

#### 🏗️ dbt on Airbyte Data

```
Create a new dbt project named dbt_airbyte_customer and generate a staging model
for the airbyte_demo_d.customer table, bound to the airbyte_teradata_profile profile
```

---

#### 🚀 Airflow — End-to-End Pipeline

```
Create an Airflow pipeline that first triggers the Airbyte sync connection created above,
then runs the dbt_airbyte_customer project after the sync completes
```

```
Deploy the generated DAG to Airflow and show me its status
```

```
Trigger the pipeline now and monitor its progress
```

---

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) — MCP server framework
- [Teradata](https://www.teradata.com/) — Data warehouse platform
- [Apache Airflow](https://airflow.apache.org/) — Workflow orchestration
- [Airbyte](https://airbyte.com/) — Data integration platform
- [dbt](https://www.getdbt.com/) — Data transformation tool
