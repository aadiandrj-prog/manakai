#!/bin/sh
set -eu

alembic -c alembic.ini upgrade head
if [ "${DEMO_MODE:-true}" = "true" ]; then
  python -m app.seed
fi
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
