#!/bin/sh
set -eu
if [ -z "${DATABASE_URL:-}" ]; then echo "DATABASE_URL is required" >&2; exit 1; fi
backup_path="${1:-}"
if [ -z "$backup_path" ]; then echo "Usage: DATABASE_URL=... $0 /explicit/path/manakai.dump" >&2; exit 1; fi
pg_dump --format=custom --no-owner --no-privileges --file="$backup_path" "$DATABASE_URL"
echo "Backup written to $backup_path"
