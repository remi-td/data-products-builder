# {{ Project Name }}

A {{ one-line description }} powered by Teradata Vantage.

## Stack
- **Backend**: FastAPI + teradatasqlalchemy (Python 3.11+)
- **Frontend**: React 18 + Vite + TypeScript + Tailwind + React Query + Recharts
- **Deploy**: Docker compose / Static (GitHub Pages) + remote API

## Quickstart

```bash
cp backend/.env.example backend/.env   # fill TD_HOST/TD_USER/TD_PASSWORD
(cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload) &
(cd frontend && npm install && npm run dev)
# open http://localhost:5173
```

See [deploy/README.md](deploy/README.md) for Docker and GitHub Pages.

## Pages

| Route       | Description                | Backend endpoint        |
|-------------|----------------------------|-------------------------|
| `/`         | Overview                   | —                       |
| `/health`   | Connection status          | `GET /api/health`       |
| ...         | ...                        | ...                     |

## Conventions

This project follows the patterns documented in the **teradata-react**
skill. Key rules:

- All SQL is parameterized (`text("... :param ...")`); never f-string.
- The SQLAlchemy engine is a singleton with `pool_pre_ping=True`.
- Routers are thin; logic lives in `backend/app/queries/`.
- Pages consume hooks from `frontend/src/lib/queries.ts`; never `fetch`.
- Brand tokens are CSS variables in `frontend/src/theme/brand.css`.
