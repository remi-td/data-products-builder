#!/usr/bin/env bash
# sanitize-sql.sh -- Replace non-ASCII characters in SQL files
#
# Teradata rejects non-ASCII chars with error 6706. LLM-generated SQL commonly
# contains em dashes, en dashes, smart quotes, and arrows that must be replaced.
#
# Usage:
#   scripts/sanitize-sql.sh file.sql              # sanitize one file (in-place)
#   scripts/sanitize-sql.sh src/revenue/**/*.sql   # sanitize multiple files
#   scripts/sanitize-sql.sh --check file.sql       # check only, don't modify (exit 1 if dirty)

set -euo pipefail

CHECK_ONLY=false
if [ "${1:-}" = "--check" ]; then
  CHECK_ONLY=true
  shift
fi

if [ $# -eq 0 ]; then
  echo "Usage: sanitize-sql.sh [--check] file.sql [file2.sql ...]" >&2
  exit 1
fi

DIRTY=0

for f in "$@"; do
  if [ ! -f "$f" ]; then
    echo "sanitize-sql: SKIP: $f (not a file)" >&2
    continue
  fi

  # Check for non-ASCII characters
  if LC_ALL=C grep -Pn '[^\x00-\x7F]' "$f" > /dev/null 2>&1; then
    if [ "$CHECK_ONLY" = true ]; then
      echo "sanitize-sql: DIRTY: $f" >&2
      LC_ALL=C grep -Pn '[^\x00-\x7F]' "$f" >&2
      DIRTY=1
    else
      # Replace common offenders in-place
      sed -i'' -e 's/\xe2\x80\x94/--/g' \
               -e 's/\xe2\x80\x93/-/g' \
               -e 's/\xe2\x86\x92/->/g' \
               -e "s/\xe2\x80\x98/'/g" \
               -e "s/\xe2\x80\x99/'/g" \
               -e "s/\xe2\x80\x9c/\"/g" \
               -e "s/\xe2\x80\x9d/\"/g" \
               "$f"

      # Catch any remaining non-ASCII
      if LC_ALL=C grep -Pn '[^\x00-\x7F]' "$f" > /dev/null 2>&1; then
        echo "sanitize-sql: WARN: $f still has non-ASCII chars after replacement:" >&2
        LC_ALL=C grep -Pn '[^\x00-\x7F]' "$f" >&2
        DIRTY=1
      else
        echo "sanitize-sql: FIXED: $f"
      fi
    fi
  else
    echo "sanitize-sql: OK: $f"
  fi
done

exit $DIRTY
