#!/bin/sh
set -eu
if [ "${CONFIRM_MANAKAI_RESTORE:-}" != "RESTORE_TO_EMPTY_DATABASE" ]; then
  echo "Refusing restore. Set CONFIRM_MANAKAI_RESTORE=RESTORE_TO_EMPTY_DATABASE after verifying the target is an empty recovery database." >&2; exit 1
fi
if [ -z "${DATABASE_URL:-}" ] || [ -z "${1:-}" ]; then echo "Usage: DATABASE_URL=... CONFIRM_MANAKAI_RESTORE=RESTORE_TO_EMPTY_DATABASE $0 /explicit/path/manakai.dump" >&2; exit 1; fi
pg_restore --exit-on-error --no-owner --no-privileges --dbname="$DATABASE_URL" "$1"
echo "Restore completed. Run alembic current and /ready checks before use."
