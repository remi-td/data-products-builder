#!/usr/bin/env bash
# deploy.sh -- Deploy a data product to Teradata in phased module order
#
# Reads SQL files from src/{product}/ and executes them using tq, following
# the deployment order: Phase 1 (01-*) then Phase 2 (02-*) then Phase 3 (03-*).
#
# Prerequisites:
#   - tq installed and on PATH
#   - TQ_LOGON set (run: source scripts/tq-connect.sh)
#
# Usage:
#   scripts/deploy.sh revenue                  # deploy the "revenue" data product
#   scripts/deploy.sh revenue --dry-run        # show what would be executed
#   scripts/deploy.sh revenue --module 02-domain  # deploy a single module only

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Args ---
PRODUCT="${1:-}"
DRY_RUN=false
MODULE_FILTER=""

shift || true
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=true ;;
    --module)  MODULE_FILTER="$2"; shift ;;
    *)         echo "deploy: Unknown option: $1" >&2; exit 1 ;;
  esac
  shift
done

if [ -z "$PRODUCT" ]; then
  echo "Usage: deploy.sh <product-name> [--dry-run] [--module <module-dir>]" >&2
  echo "" >&2
  echo "Available products:" >&2
  ls -d "$PROJECT_ROOT/src"/*/ 2>/dev/null | xargs -I{} basename {} >&2
  exit 1
fi

SRC_DIR="$PROJECT_ROOT/src/$PRODUCT"
if [ ! -d "$SRC_DIR" ]; then
  echo "deploy: ERROR: $SRC_DIR does not exist" >&2
  exit 1
fi

# --- Preflight checks ---
if [ -z "${TQ_LOGON:-}" ]; then
  echo "deploy: ERROR: TQ_LOGON is not set. Run: source scripts/tq-connect.sh" >&2
  exit 1
fi

if ! command -v tq &> /dev/null; then
  echo "deploy: ERROR: tq not found on PATH. Install it first." >&2
  exit 1
fi

# --- Sanitize all SQL files ---
echo "deploy: Sanitizing SQL files..."
"$SCRIPT_DIR/sanitize-sql.sh" "$SRC_DIR"/*/*.sql

# --- Discover and sort modules ---
# Modules are directories like 01-memory, 01-semantic, 02-domain, etc.
# Sort by directory name to respect phase ordering.
if [ -n "$MODULE_FILTER" ]; then
  MODULES=("$SRC_DIR/$MODULE_FILTER")
else
  MODULES=($(ls -d "$SRC_DIR"/*/ 2>/dev/null | sort))
fi

# --- Deploy ---
TOTAL_FILES=0
TOTAL_OK=0

for module_dir in "${MODULES[@]}"; do
  module_name=$(basename "$module_dir")
  echo ""
  echo "========================================"
  echo "deploy: Module: $module_name"
  echo "========================================"

  # Execute SQL files in numbered order
  for sql_file in $(ls "$module_dir"/*.sql 2>/dev/null | sort); do
    file_name=$(basename "$sql_file")
    TOTAL_FILES=$((TOTAL_FILES + 1))

    if [ "$DRY_RUN" = true ]; then
      echo "  [DRY-RUN] $module_name/$file_name"
      TOTAL_OK=$((TOTAL_OK + 1))
    else
      echo "  --- $module_name/$file_name ---"
      if tq query --file "$sql_file"; then
        echo "  OK"
        TOTAL_OK=$((TOTAL_OK + 1))
      else
        echo "deploy: FAILED at $module_name/$file_name" >&2
        echo "deploy: $TOTAL_OK/$TOTAL_FILES files succeeded before failure." >&2
        exit 1
      fi
    fi
  done
done

echo ""
echo "========================================"
if [ "$DRY_RUN" = true ]; then
  echo "deploy: DRY-RUN complete. $TOTAL_FILES files would be executed."
else
  echo "deploy: SUCCESS. $TOTAL_OK/$TOTAL_FILES files executed."
fi
echo "========================================"
