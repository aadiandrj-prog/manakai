# Staging deployment

Phase 2D targets one integrated public staging environment:

```text
Sites frontend (HTTPS)
→ Render FastAPI service (HTTPS)
→ private Render PostgreSQL 16 + pgvector
→ one configured OpenAI or Gemini model provider
```

`render.yaml` declares the API, private managed database and daily authoritative-source change check. The API pre-deploy command runs Alembic once and idempotently ingests the authoritative kettle snapshot. `/health` is process liveness; `/ready` verifies the database, exact Alembic revision and authoritative kettle records.

## Account-owner deployment steps

1. In Render, create a Blueprint from this repository and review the paid staging plans before approving charges.
2. Enter exactly one provider configuration: `LLM_PROVIDER=openai`, an approved `LLM_MODEL` and `OPENAI_API_KEY`, or the Gemini equivalents. Never put keys in Git or logs.
3. Wait for pre-deploy and `/ready` to pass. Record the HTTPS API URL.
4. Set Sites build variables `NEXT_PUBLIC_API_URL=https://<render-api-host>` and `NEXT_PUBLIC_APP_ENV=staging`, then publish.
5. Change `CORS_ORIGINS` only if the final Sites origin differs from `https://manakai-sih26.aadiandrj.chatgpt.site`.
6. Run `STAGING.md` and one real-provider evaluation. Do not call the milestone complete until they pass.

The repository cannot create paid infrastructure or model credentials without the account owner. A frontend-only publish is deliberately rejected because it would expose a broken integrated flow.

## Migration, rollback and backup

Every schema change is a new Alembic revision. Render runs `alembic upgrade head` as a single pre-deploy operation before traffic moves. Revision `b48f761da923` is additive. Do not edit deployed migration history.

Redeploy the previous image only when it is compatible with the additive schema. Database downgrade is not the normal rollback. Restore into a separate recovery database, validate it, and switch deliberately.

Use a paid managed database with backups/PITR. `scripts/backup_staging.sh` adds an explicit custom-format dump; `scripts/restore_staging.sh` refuses to run without confirmation that the target is an empty recovery database. Test restore quarterly.
