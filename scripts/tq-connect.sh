#!/usr/bin/env bash
# tq-connect.sh -- Set TQ_LOGON and TQ_LOGMECH from config/environments.yaml
#
# Usage:
#   source scripts/tq-connect.sh          # connect to the default (target) environment
#   source scripts/tq-connect.sh prod     # connect to a specific environment
#
# Must be sourced (not executed) so the exported variables persist in your shell.

# Resolve project root (works in both bash and zsh, sourced or executed)
if [ -n "${BASH_SOURCE[0]:-}" ]; then
  _TQ_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [ -n "${(%):-%x}" 2>/dev/null ]; then
  _TQ_SCRIPT_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd)"
else
  _TQ_SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi
PROJECT_ROOT="$(cd "$_TQ_SCRIPT_DIR/.." && pwd)"
CONFIG="$PROJECT_ROOT/config/environments.yaml"

if [ ! -f "$CONFIG" ]; then
  echo "tq-connect: ERROR: $CONFIG not found." >&2
  echo "tq-connect: Run: cp config/environments.yaml.example config/environments.yaml" >&2
  return 1 2>/dev/null || exit 1
fi

# Determine which environment to use
ENV_NAME="${1:-}"
if [ -z "$ENV_NAME" ]; then
  ENV_NAME=$(grep '^target:' "$CONFIG" | head -1 | awk '{print $2}')
fi

if [ -z "$ENV_NAME" ]; then
  echo "tq-connect: ERROR: No environment specified and no 'target' key in $CONFIG" >&2
  return 1 2>/dev/null || exit 1
fi

# Parse YAML (simple awk -- no external deps)
# Extracts key: value pairs from the named environment block
parse_env() {
  local key="$1"
  awk -v env="$ENV_NAME" -v key="$key" '
    /^  [a-zA-Z]/ { current_env = $1; gsub(/:/, "", current_env) }
    current_env == env && $1 == key":" { print $2 }
  ' "$CONFIG"
}

HOST=$(parse_env host)
PORT=$(parse_env port)
DATABASE=$(parse_env database)
USER=$(parse_env user)
PASSWORD=$(parse_env password)
LOGMECH=$(parse_env logmech)

if [ -z "$HOST" ] || [ -z "$USER" ] || [ -z "$PASSWORD" ]; then
  echo "tq-connect: ERROR: Could not parse environment '$ENV_NAME' from $CONFIG" >&2
  echo "tq-connect: Check that the environment exists and has host, user, password fields." >&2
  return 1 2>/dev/null || exit 1
fi

PORT="${PORT:-1025}"
LOGMECH="${LOGMECH:-TD2}"

export TQ_LOGON="${USER}:${PASSWORD}@${HOST}:${PORT}/${DATABASE}"
export TQ_LOGMECH="${LOGMECH}"

# Add tq to PATH if installed locally
if [ -d "$PROJECT_ROOT/scripts/tq/bin" ]; then
  export PATH="$PROJECT_ROOT/scripts/tq/bin:$PATH"
fi

echo "tq-connect: Connected to '$ENV_NAME' (${HOST}:${PORT}/${DATABASE}) as ${USER}"
