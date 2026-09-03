#!/bin/sh
set -eu

# Render's free service has no pre-deploy command. These operations are safe to
# repeat and guarantee that readiness never succeeds with an empty database.
alembic -c alembic.ini upgrade head
python -m app.ingestion electric-kettle

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers --forwarded-allow-ips="*"
