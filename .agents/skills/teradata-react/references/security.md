# Security & Hardening

Apply every item before shipping outside a sandbox.

## 1. Parameterize all SQL

**Always** use SQLAlchemy `text(...)` with `:named` params. Never build
SQL with `f""`, `.format()`, or `+`.

```python
# WRONG — SQL injection
db.execute(text(f"SELECT * FROM dbc.tablesV WHERE databasename = '{database}'"))

# RIGHT
db.execute(text("SELECT * FROM dbc.tablesV WHERE databasename = :db"), {"db": database})
```

If you need a *dynamic identifier* (table name, column name), allowlist
it server-side:

```python
ALLOWED_VIEWS = {"tablesV", "databasesV", "diskspaceV"}
def get_view(name: str) -> str:
    if name not in ALLOWED_VIEWS:
        raise HTTPException(400, "unknown view")
    return name
```

## 2. Database user scope

Create a dedicated, **read-only** Teradata user for the app. Never use a
DBA/superuser credential. Grant only the views the app needs.

```sql
CREATE USER td_react_app AS PERM = 0, PASSWORD = '...';
GRANT SELECT ON dbc.tablesV  TO td_react_app;
GRANT SELECT ON dbc.databasesV TO td_react_app;
```

If the app writes, use a *separate* user with `INSERT`/`UPDATE` on the
specific target tables, and a *separate* router that depends on a
write-scoped session factory.

## 3. Secrets

- `.env` file for local dev; never commit.
- Production: inject via your platform's secret manager (AWS SM, GCP
  SM, k8s Secret).
- `settings.py` reads from env only:

```python
class Settings(BaseSettings):
    td_host: str
    td_user: str
    td_password: SecretStr
    td_logmech: str = "TD2"
    model_config = SettingsConfigDict(env_file=".env", env_prefix="")
```

- Never log `settings.td_password.get_secret_value()`.

## 4. CORS

Whitelist origins explicitly. `allow_origins=["*"]` is acceptable only
during local dev:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,   # ["https://app.example.com"]
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 5. Authentication

Out of scope for the bare template (most demos run behind VPN/SSO at
the edge). When you need it, prefer:
- **Reverse-proxy auth** (Cloudflare Access, IAP, oauth2-proxy) —
  zero app code.
- **Bearer JWT** validated in a FastAPI dependency for self-contained
  deployments.

Never roll your own session cookie scheme.

## 6. Rate limiting

Add `slowapi` or rely on an upstream (Cloudflare, NGINX). Teradata
sessions are expensive; an unauthenticated `/api/tables` is a free DOS
amplifier.

## 7. Input validation

Pydantic models on requests, `Query(..., min_length=…, max_length=…,
regex=…)` on query params. Reject before the DB call.

## 8. Response shaping

Pydantic response models prevent accidental leakage of internal
columns (e.g. row counts on system tables that hint at data volume).

## 9. Static asset hosting

If you ship the SPA on GitHub Pages, the `VITE_API_URL` is **public**.
That's fine — but the API must enforce auth & rate limits as if the
client were untrusted (because it is).

## 10. Dependency hygiene

- `pip-tools` or `uv` lock file for backend.
- `npm audit --omit=dev` clean before release.
- Renovate / Dependabot enabled.
