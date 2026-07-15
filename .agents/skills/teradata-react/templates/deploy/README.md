# Deployment

Three supported topologies — same source tree, different commands.

## 1. Local dev

```bash
# terminal 1
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # then fill TD_HOST/TD_USER/TD_PASSWORD
uvicorn app.main:app --reload

# terminal 2
cd frontend
npm install
npm run dev                # http://localhost:5173
```

Vite proxies `/api/*` to `http://localhost:8000`, so `VITE_API_URL`
isn't needed in dev.

## 2. Docker / docker-compose

```bash
cp backend/.env.example backend/.env   # fill secrets
docker compose -f deploy/docker-compose.yml up --build
# frontend: http://localhost:8080
```

`nginx` in the frontend container reverse-proxies `/api/` to the
backend container. The backend isn't exposed to the host.

## 3. Static site + remote API

Use when you want zero ops on the frontend:

1. Deploy the backend container anywhere (Cloud Run, Fly.io, ECS,
   on-prem). Note its HTTPS URL (e.g. `https://api.example.com`).
2. In the GitHub repo, set:
   - `vars.VITE_API_URL` = `https://api.example.com`
   - Pages source = "GitHub Actions"
3. Copy `github-pages.yml` to `.github/workflows/`.
4. Push to `main`. The action builds the SPA and publishes to Pages.

Update the backend's `CORS_ORIGINS` to include the Pages URL.

## Hardening checklist before shipping

- [ ] Dedicated read-only Teradata user (`security.md` §2).
- [ ] Secrets in env / secret manager, never committed.
- [ ] `CORS_ORIGINS` whitelist, not `*`.
- [ ] Auth at the edge (reverse proxy / IAP / Cloudflare Access) or
      JWT dependency on routers.
- [ ] Rate limiting (slowapi or upstream).
- [ ] HTTPS terminated upstream; HSTS header set.
- [ ] Container scanned (`docker scout` / Trivy) and Renovate/Dependabot
      enabled.
