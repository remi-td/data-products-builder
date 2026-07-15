# Teradata SQL Kernel — Magic commands reference

The Teradata SQL Kernel (`teradatasql`) accepts SQL directly in code cells. It also
supports a set of `%` magic commands for connection management, variables,
data loading, history, visualization, and help.

Run `%help` in a notebook to see the live list on the installed kernel; `%help <name>` (without the `%`) prints help for a specific magic.

For parameterized magics (`name=value, name2=value2`):
- parameter names are case-insensitive
- values may be quoted with `"..."`; quoting is only required when the value contains `,`, `=`, `"`, `\`, or a newline

Variable substitution: `${name}` is expanded inside SQL and magic arguments after running `%var ...`.

---

## Connections

| Magic | Purpose | Example |
|---|---|---|
| `%lsconnect` | List defined connections. `*` marks the active one. | `%lsconnect` |
| `%addconnect` | Register a new connection profile. | `%addconnect name=prod, user=dbc, host=td.example.com, database=salesdb` |
| `%chconnect` | Edit an existing connection. | `%help chconnect` |
| `%rmconnect` | Remove a connection. | `%rmconnect name=prod` |
| `%connect` | Connect to or switch the active connection. Prompts for password on first connect. | `%connect prod` |
| `%disconnect` | Disconnect a connection. | `%disconnect prod` |
| `%%connect` | **Cell magic.** Run the SQL in the same cell on the specified connection without changing the active connection. | `%%connect prod`<br>`SELECT TOP 5 * FROM demo;` |
| `%currentdb` | Show the current database on the active connection. | `%currentdb` |

### `%addconnect` parameters

| Name | Required | Notes |
|---|---|---|
| `name` | yes | Connection label used by `%connect`. |
| `host` | yes | Hostname or IP of the Teradata system. |
| `user` | no | If omitted, `%connect` prompts for it. |
| `database` | no | Default database to set after connect. |
| `logmech` | no | `TD2` (default), `LDAP`, `KRB5`, `BROWSER`, `TDNEGO`. |
| `logdata` | no | Extra auth data for the chosen mechanism. |
| `sslmode` | no | `DISABLE` / `ALLOW` / `PREFER` (default) / `REQUIRE` / `VERIFY-CA` / `VERIFY-FULL`. |

See `reference/connections.md` for the full connection parameter table.

---

## Variables

| Magic | Purpose |
|---|---|
| `%var name=value, name2=value2` | Define one or more session variables. |
| `%lsvar` | List defined variables. |
| `%rmvar name` | Remove a variable. |

Substitute anywhere in SQL or magic args with `${name}`:

```sql
%var db=salesdb, t=orders
SELECT TOP 10 * FROM ${db}.${t};
```

Variables are the primary mechanism for parameterizing notebooks — prefer them over hardcoded literals.

---

## Data load

`%dataload` ingests a local CSV into an existing table.

```
%dataload DATABASE=<db>, TABLE=<table>, FILEPATH=<path-to-csv>
```

Parameters:
- `DATABASE` — target database
- `TABLE` — target table (must already exist with compatible columns)
- `FILEPATH` — path to the CSV, relative to the JupyterLab working directory

`%help dataload` shows all options including delimiter, quote, header handling.

---

## History and result sets

Every executed cell produces a history entry. Non-error SQL that returns rows also produces a **result set** with an ID (shown in `<...>` in `%history` output).

| Magic | Purpose | Example |
|---|---|---|
| `%history` | Show last 20 history items. | `%history` |
| `%history N` | Show last N items. | `%history 5` |
| `%history START,N` | Show N items starting at id START. | `%history 7,35` |
| `%history id=N` | Show detailed entry for a specific id. | `%history id=75` |
| `%history all` | Show everything. | `%history all` |
| `%history status=...,command=...,connection=...` | Filter by any combination. | `%history status=success,command=select` |
| `%rmhistory N` | Remove a history entry. | `%rmhistory 40` |
| `%table N` | Re-display the result set with id N. | `%table 10` |

Result set CSV files are stored under `Teradata/ResultSets/<timestamp>/` in the JupyterLab working directory, making them easy to load into a pandas/R notebook.

---

## Visualization — `%chart`

`%chart` renders a [Vega-Lite](https://vega.github.io/vega-lite/) visualization from a result set.

```
%chart <x-column>, <y-column> [, option=value, ...]
```

Options:

| Option | Default | Description |
|---|---|---|
| `id` | most recent result set | History / result set id to plot. |
| `title` | *(none)* | Chart title. |
| `mark` | `bar` | `bar` / `line` / `area` / `point` / `rect` / `square` / `text` / `tick`. |
| `typex` / `typey` | auto | Vega-Lite type: `n` (nominal), `o` (ordinal), `q` (quantitative), `t` (temporal). Use `typey=q` when numeric columns come in as strings. |
| `labelx` / `labely` | column name | Axis labels. |
| `gridx` / `gridy` | `true` | Show/hide gridlines. |

Examples:

```
%chart region, total, title=Revenue by Region
%chart sale_dt, daily_total, mark=line, typex=t, title=Daily Sales
%chart x=id, y=point1, typey=q        -- explicit x=/y= form also works
%chart region, total, id=42           -- plot a specific past result set
```

---

## Other

| Magic | Purpose |
|---|---|
| `%help` / `%help <name>` | Show all magics / help for one magic. |
| `%lsmagic` | List magic names without descriptions. |
| `%pyinfo [prefix]` | Show Python version + modules installed on the connected Teradata system. |
| `%rinfo [prefix]` | Same, for R. |

### Snippets

Typing a SQL keyword followed by `?` in its own cell (e.g. `CREATE?`, `MACRO?`, `UPDATE?`) and running it prints a template snippet you can copy into the next cell.

`%help snippets` lists all available snippet keywords.
