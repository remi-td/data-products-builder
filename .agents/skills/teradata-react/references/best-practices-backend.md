# Backend Best Practices (FastAPI + teradatasqlalchemy)

Read this before writing or reviewing backend code. Snippets are
copy-pasteable into a project scaffolded from `templates/backend/`.

## Launching uvicorn from a shell script

Use a subshell `cd` — never `--app-dir`. The `--app-dir` flag adds the
directory to Python's `sys.path` so `import app` resolves, but it does **not**
change the working directory. pydantic-settings resolves `env_file=".env"`
relative to CWD, which stays at the caller's location (usually the repo root)
when launched from a top-level script. The `.env` is silently skipped and all
required fields raise `ValidationError` at startup.

```bash
# WRONG — CWD stays at repo root; .env is not found
"$BACKEND/.venv/bin/uvicorn" app.main:app --port 8000 --app-dir "$BACKEND" &

# CORRECT — CWD is $BACKEND; .env is found; sys.path is handled automatically
(cd "$BACKEND" && ".venv/bin/uvicorn" app.main:app --port 8000) &
BACKEND_PID=$!
```

The canonical single-command dev launcher pattern (copy to `start.sh` at
project root — see `templates/start.sh`):

```bash
#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$REPO/backend"
FRONTEND="$REPO/frontend"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

# Fail fast if ports are already occupied — prevents silent drift
check_port() {
  if lsof -ti :"$1" >/dev/null 2>&1; then
    echo "ERROR: port $1 in use. Set BACKEND_PORT/FRONTEND_PORT and retry." >&2; exit 1
  fi
}
check_port "$BACKEND_PORT"
check_port "$FRONTEND_PORT"

cleanup() { kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

[ -d "$BACKEND/.venv" ] || python3 -m venv "$BACKEND/.venv"
"$BACKEND/.venv/bin/pip" install -q -r "$BACKEND/requirements.txt"
(cd "$BACKEND" && ".venv/bin/uvicorn" app.main:app --port "$BACKEND_PORT" --reload) &
BACKEND_PID=$!
echo "Backend starting → http://localhost:$BACKEND_PORT/docs"

[ -d "$FRONTEND/node_modules" ] || npm --prefix "$FRONTEND" install --silent
VITE_BACKEND_PORT="$BACKEND_PORT" VITE_FRONTEND_PORT="$FRONTEND_PORT" \
  npm --prefix "$FRONTEND" run dev &
FRONTEND_PID=$!
echo "Frontend starting → http://localhost:$FRONTEND_PORT"

wait
```

## Credentials and .env bootstrapping

Before writing any `.env`, check whether a `DATABASE_URI` environment
variable exists in the user's shell. This URI scheme is used by the
Teradata MCP server and Jupyter demos and is becoming a common convention:

```
teradata://<USERNAME>:<PASSWORD>@<HOST>:1025/<SCHEMA>
```

If present, **offer** to derive the individual fields from it — never
apply it silently, because the URI may target a different environment:

> *"I see `DATABASE_URI` pointing to `<HOST>`. Use this connection?"*

Parse carefully — the URI port (1025) is embedded in
`get_connection_url()`, not stored as a separate setting; the path
component maps to `TD_DEFAULT_DATABASE`:

```python
from urllib.parse import urlparse
u = urlparse(os.environ["DATABASE_URI"])
# u.scheme == "teradata", u.port == 1025
TD_USER             = u.username
TD_PASSWORD         = u.password          # never log
TD_HOST             = u.hostname
TD_DEFAULT_DATABASE = u.path.lstrip("/")  # e.g. "data_engineer" or "MYSCHEMA"
```

If `DATABASE_URI` is absent, emit explicit placeholders and ask:

```ini
# backend/.env  — fill before running
TD_HOST=CHANGE_ME
TD_USER=CHANGE_ME
TD_PASSWORD=CHANGE_ME
TD_DEFAULT_DATABASE=CHANGE_ME
```

**Never guess** that the password matches the username or the project
name. Always ask. `TD_DEFAULT_DATABASE` is frequently different from
`TD_USER` (e.g., a shared schema name), so confirm it separately.

## Connection pooling

Create the engine **once** and reuse it. Use `settings.get_connection_url()` —
it centralizes URL construction from `TD_HOST/TD_USER/TD_PASSWORD` and keeps
the dialect scheme (`teradatasql://`) in one place.

**Dialect quirk:** `teradatasqlalchemy` defaults to `SingletonThreadPool`,
which does not accept `pool_size` or `max_overflow` and gives no bound on
concurrent Teradata sessions. Override with `poolclass=QueuePool` to get
controlled, counted pooling. The `teradatasql` driver is thread-safe and works
correctly with `QueuePool`.

```python
# app/db/engine.py
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from app.settings import settings

@lru_cache(maxsize=1)
def get_engine() -> Engine:
    # Override SingletonThreadPool with QueuePool — Teradata sessions are a
    # licensed resource; pool_size + max_overflow is the hard ceiling.
    return create_engine(
        settings.get_connection_url(),
        poolclass=QueuePool,
        pool_size=5,        # tune to expected concurrency
        max_overflow=5,     # absorb spikes; total ceiling = 10 sessions
        pool_pre_ping=True,
        pool_recycle=1800,
        future=True,
    )
```

**Why each setting:**
- `poolclass=QueuePool`: overrides the dialect default so `pool_size` and
  `max_overflow` are respected. Without this they raise `TypeError`.
- `pool_size + max_overflow`: upper bound on Teradata sessions. Set with DBA
  awareness; do not exceed your workload's allotted session count.
- `pool_pre_ping`: Teradata gateways drop idle sessions; without this
  you'll see `SocketException` on the first request after idle.
- `pool_recycle`: belt-and-suspenders for `pre_ping` on long-running pods.

## Sessions via FastAPI dependency

**IMPORTANT:** Do NOT create `SessionLocal` at module level. Doing so calls
`get_engine()` at import time, before `uvicorn` has loaded the `.env` file,
causing a startup crash. Create it inside `get_db()` instead.

```python
# app/db/session.py
from sqlalchemy.orm import Session, sessionmaker
from app.db.engine import get_engine

def get_db():
    # SessionLocal built here so get_engine() runs after .env is loaded
    SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False, future=True)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Query module pattern

Keep each query in `app/queries/<resource>.py`. SQL lives next to the
function that runs it, not in the router.

```python
# app/queries/tables.py
from sqlalchemy import text
from sqlalchemy.orm import Session

LIST_BY_DATABASE = text("""
    SELECT  databasename, tablename, tablekind, createtimestamp
    FROM    dbc.tablesV
    WHERE   databasename = :db
    ORDER BY tablename
    SAMPLE  :limit
""")

def list_by_database(db: Session, database: str, limit: int = 100):
    rows = db.execute(LIST_BY_DATABASE, {"db": database, "limit": limit}).mappings().all()
    return list(rows)
```

**Rules:**
- `text(...)` constants at module top with `:named` params only.
- Functions take a `Session` and primitives. No `Request`, no Pydantic
  models in `queries/` — they belong in the router boundary.
- Return plain lists/dicts; let Pydantic shape them in the router.

## Routers stay thin

```python
# app/routers/tables.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.queries import tables as q
from app.schemas import TableRow

router = APIRouter(prefix="/api/tables", tags=["tables"])

@router.get("", response_model=list[TableRow])
def list_tables(database: str = Query(..., min_length=1, max_length=128),
                limit: int = Query(100, ge=1, le=10000),
                db: Session = Depends(get_db)):
    return q.list_by_database(db, database, limit)
```

## Pagination

Default to `SAMPLE n` or `TOP n` for fast previews; switch to keyset
pagination for stable scrolling:

```sql
SELECT  ...
FROM    big.fact
WHERE   id > :after
ORDER BY id
SAMPLE  :limit
```

Avoid `OFFSET`-based pagination on Teradata; it forces re-scanning.

## Caching

In-process TTL cache for read-mostly endpoints:

```python
# app/cache.py
from cachetools import TTLCache
from functools import wraps

_cache = TTLCache(maxsize=512, ttl=60)

def ttl_cached(key_fn):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            k = key_fn(*a, **kw)
            if k in _cache:
                return _cache[k]
            v = fn(*a, **kw)
            _cache[k] = v
            return v
        return wrapper
    return deco
```

Apply at the query layer, not the router:

```python
@ttl_cached(lambda db, database, limit=100: ("tables", database, limit))
def list_by_database(db, database, limit=100):
    ...
```

For multi-replica deployments, swap to Redis.

## Error handling

- Don't swallow `OperationalError` — log with the query name and
  parameters (mask secrets), return 503.
- Validate inputs at the router with Pydantic / `Query(...)` constraints
  *before* hitting the database.

```python
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError, DBAPIError

@router.get(...)
def list_tables(...):
    try:
        return q.list_by_database(db, database, limit)
    except OperationalError as e:
        logger.exception("td.tables.list_by_database failed db=%s", database)
        raise HTTPException(status_code=503, detail="Database unavailable")
```

## Logging

Use `structlog` or `logging` with a request-id middleware. Always log:
- query name (not full SQL)
- parameter keys (not values, unless safe)
- elapsed ms
- row count

## Async vs sync

`teradatasqlalchemy` is a sync driver. Use **sync** route functions and
let FastAPI's threadpool handle concurrency. Mixing `async def` with
sync DB calls blocks the event loop.

```python
@router.get("")           # sync def — correct
def list_tables(...): ...

# Avoid:
@router.get("")
async def list_tables(...):  # would block event loop on db.execute
    ...
```

## dbc.* view quirks

When querying Teradata system views (`dbc.DiskSpaceV`, `dbc.DatabasesV`,
`dbc.TablesV`, etc.), watch for two common pitfalls:

**1. GROUP BY position references rejected on DiskSpaceV**

`GROUP BY 1` is rejected on `dbc.DiskSpaceV` with Error 3504. Use the
column name explicitly:

```sql
-- Wrong (Error 3504):
SELECT TRIM(databasename), SUM(currentperm) FROM dbc.DiskSpaceV GROUP BY 1

-- Correct:
SELECT  TRIM(databasename) AS databasename,
        SUM(currentperm)   AS currentperm
FROM    dbc.DiskSpaceV
GROUP BY databasename
ORDER BY SUM(currentperm) DESC
```

**2. Mixed-case column names from dbc.DatabasesV**

`dbc.DatabasesV` returns `PermSpace`, `SpoolSpace`, `TempSpace` with
capital letters. SQLAlchemy `.mappings()` preserves the case, so Pydantic
will fail validation if your schema uses lowercase field names.
Always alias to lowercase in the SELECT:

```sql
SELECT  TRIM(databasename) AS databasename,
        PermSpace          AS permspace,
        SpoolSpace         AS spoolspace,
        TempSpace          AS tempspace
FROM    dbc.DatabasesV
```

## Teradata SQL gotchas in application queries

These trip up most dashboards. Handle them up front in query design.

**1. Alias ambiguity**

Ambiguous aliases (e.g., the
same name appears in multiple joined or aggregated scopes) do not pose problem in query development but often do in dashboards dynamic aggregation. This is
particularly common in dynamic `ORDER BY` or `GROUP BY`clauses.

```sql
-- Fragile — alias "score" may clash in a complex aggregation:
SELECT supplier_id, SUM(risk_weight) AS risk_weight
FROM facts
GROUP BY supplier_id
ORDER BY risk_weight DESC;   -- may raise "ambiguous" error in some contexts

-- Safe — use the expression directly, or wrap in a CTE:
WITH base AS (
    SELECT supplier_id, SUM(risk_weight) AS risk_weight
    FROM facts
    GROUP BY supplier_id
)
SELECT supplier_id, risk_weight FROM base ORDER BY risk_weight DESC;

-- Safe — explicit metric calculation name:
SELECT supplier_id, SUM(risk_weight) AS risk_weight_sum, AVG(risk_weight) AS risk_weight_avg
FROM facts
GROUP BY supplier_id
ORDER BY risk_weight_sum DESC   -- may raise "ambiguous" error in some contexts

```

**2. Prefer aggregate CTEs over complex grouped final joins**

When a query joins aggregated results to lookup tables, isolate the
aggregation in a CTE first rather than aggregating inside a join. This
avoids the common alias errors or source confusion when multiple tables have overlapping column names:

```sql
-- Problematic pattern:
SELECT s.name, SUM(f.amount) AS total
FROM suppliers s JOIN facts f ON s.id = f.supplier_id
GROUP BY s.name
ORDER BY total DESC

-- Safer pattern:
WITH supplier_totals AS (
    SELECT supplier_id, SUM(amount) AS total
    FROM facts
    GROUP BY supplier_id
)
SELECT s.name, t.total
FROM suppliers s JOIN supplier_totals t ON s.id = t.supplier_id
ORDER BY t.total DESC
```

## Testing

- Unit-test `queries/*` against a real (test) Teradata or a recorded
  fixture. Don't mock SQLAlchemy — the seams are too narrow.
- Use FastAPI `TestClient` for router shape tests with a fake `get_db`
  override returning canned data.
