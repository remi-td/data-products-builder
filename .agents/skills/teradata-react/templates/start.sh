#!/usr/bin/env bash
# Single-command dev launcher — starts backend (uvicorn) and frontend (vite) together.
# Usage: ./start.sh
# Override ports: BACKEND_PORT=9000 FRONTEND_PORT=5200 ./start.sh
# Stop: Ctrl-C (both processes are killed automatically via the trap below).
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$REPO/backend"
FRONTEND="$REPO/frontend"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

# --- Port preflight: fail fast rather than silently drift to another port ---
check_port() {
  if lsof -ti :"$1" >/dev/null 2>&1; then
    echo "ERROR: port $1 is already in use." >&2
    echo "  Set BACKEND_PORT / FRONTEND_PORT to free ports and retry." >&2
    exit 1
  fi
}
check_port "$BACKEND_PORT"
check_port "$FRONTEND_PORT"

cleanup() {
  echo ""
  echo "Stopping..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# --- Backend ---
if [ ! -d "$BACKEND/.venv" ]; then
  echo "Creating Python venv..."
  python3 -m venv "$BACKEND/.venv"
fi
"$BACKEND/.venv/bin/pip" install -q -r "$BACKEND/requirements.txt"

# NOTE: use (cd "$BACKEND" && uvicorn ...) — not --app-dir.
# --app-dir sets sys.path but does NOT change CWD, so pydantic-settings
# cannot find the relative .env file.
(cd "$BACKEND" && ".venv/bin/uvicorn" app.main:app --port "$BACKEND_PORT" --reload) &
BACKEND_PID=$!
echo "Backend starting → http://localhost:$BACKEND_PORT/docs  (PID $BACKEND_PID)"

# --- Frontend ---
if [ ! -d "$FRONTEND/node_modules" ]; then
  echo "Installing npm dependencies..."
  npm --prefix "$FRONTEND" install --silent
fi

# Pass ports to Vite via env so vite.config.ts picks them up.
# strictPort: true in vite.config.ts ensures Vite exits rather than drifting to another port.
VITE_BACKEND_PORT="$BACKEND_PORT" VITE_FRONTEND_PORT="$FRONTEND_PORT" \
  npm --prefix "$FRONTEND" run dev &
FRONTEND_PID=$!
echo "Frontend starting → http://localhost:$FRONTEND_PORT  (PID $FRONTEND_PID)"

wait
