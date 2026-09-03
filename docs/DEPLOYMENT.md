# Free staging deployment

Phase 2D uses one integrated public preview:

```text
Vercel Next.js frontend (HTTPS)
→ Render Free FastAPI service (HTTPS)
→ Neon Free PostgreSQL + pgvector
→ one tightly limited OpenAI or Gemini provider
```

Free services can sleep, throttle or change their allowances. This topology is suitable for team review and a small pilot, not a production SLA. The Render API may have a cold start after inactivity, and free database plans do not replace independent backups.

## 1. Neon database

1. Create a free PostgreSQL project in a region near the Render service.
2. Copy its pooled connection string and retain `sslmode=require`.
3. Keep this value secret. It becomes Render's `DATABASE_URL` and the GitHub repository secret `NEON_DATABASE_URL`.
4. Render startup runs `alembic upgrade head` and the idempotent electric-kettle ingestion. The migration enables `vector`; `/ready` verifies revision `b48f761da923` and authoritative records.

## 2. Render API

Create a Blueprint from this repository's `render.yaml`. It declares only one `free` Docker web service and deliberately contains no Render database or paid cron worker.

Required secret/manual values:

```text
DATABASE_URL=<Neon pooled connection string>
CORS_ORIGINS=https://<final-vercel-production-host>
LLM_PROVIDER=disabled
LLM_MODEL=
OPENAI_API_KEY=
GEMINI_API_KEY=
```

Start with the provider disabled. After deployment, confirm `/health` and `/ready`, then record the public `onrender.com` API URL. Render startup is repeatable: it applies additive migrations, performs hash-aware captured-data ingestion and then starts Uvicorn.

## 3. Vercel frontend

Import the GitHub repository as a Vercel Next.js project. The repository root is the frontend root and `vercel.json` selects native Next.js.

Set these Production and Preview environment values before deploying:

```text
NEXT_PUBLIC_API_URL=https://<render-api-host>
NEXT_PUBLIC_APP_ENV=staging
NEXT_PUBLIC_SITE_URL=https://<final-vercel-production-host>
```

These values are public by design and must never contain database or model credentials. Once the production hostname is known, update Render's `CORS_ORIGINS` to that exact origin and redeploy the API.

## 4. Scheduled source check

In GitHub, add the Actions secret `NEON_DATABASE_URL` using the same Neon connection string. `.github/workflows/regulatory-refresh.yml` runs daily at 02:30 UTC and can also be dispatched manually.

The workflow fetches allow-listed official pages, records changed hashes as `REVIEW_REQUIRED`, preserves the last verified regulatory graph and exits visibly when review is needed. It never auto-publishes changed regulatory facts.

## 5. Tightly limited provider

After the deterministic public flow passes, configure exactly one provider in Render:

```text
LLM_PROVIDER=openai
LLM_MODEL=gpt-5-mini
OPENAI_API_KEY=<secret>
```

or:

```text
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.7-flash
GEMINI_API_KEY=<secret>
```

Staging is capped at 40 provider calls per UTC day, 500 output tokens per call, 8,000 input characters, zero automatic retries, ten chat requests per minute per client and twenty analysis requests per minute per client. Usage events store provider/model/token/validation metadata but not prompt bodies or secrets. Provider failure or quota exhaustion falls back to deterministic output.

## Release order

1. Create Neon and retain the connection string securely.
2. Deploy Render with AI disabled and a temporary exact CORS value; validate `/ready`.
3. deploy Vercel with the Render URL.
4. replace Render CORS with the final Vercel origin and smoke-test the public flow.
5. add one provider secret, redeploy and run the real-provider evaluation.
6. add the GitHub Actions secret, dispatch the refresh once and inspect the run.

## Migration, rollback and backup

Every schema change is a new Alembic revision. Revision `b48f761da923` is additive. Do not edit deployed migration history. Redeploy an older image only when it remains compatible with the current schema; database downgrade is not the normal rollback.

`scripts/backup_staging.sh` creates an explicit custom-format PostgreSQL dump. `scripts/restore_staging.sh` refuses to run without confirmation that the destination is an empty recovery database. Free hosting has no production recovery guarantee, so make a local encrypted backup before each authoritative-data change.
