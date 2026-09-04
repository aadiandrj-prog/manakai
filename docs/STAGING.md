# Public staging runbook

## Required configuration

- `APP_ENV=staging`, `DEMO_MODE=false`
- managed `DATABASE_URL`; no public database allow-list
- exact Vercel production origin in Render `CORS_ORIGINS`
- `EXPECTED_SCHEMA_REVISION=f3c8a1d2e740`
- one provider/model/key combination from the allow-list
- bounded request, AI input/output, daily request and anonymous rate limits

The UI must show the staging banner and regulatory disclaimer. Records stay labelled `AUTHORITATIVE`, `VERIFIED_DERIVED`, `DEMO` or `UNVERIFIED`; modes are never silently merged.

## Release smoke checklist

1. `/health` returns 200 without querying the database; `/ready` returns revision `f3c8a1d2e740` and five coverage records.
2. Submit “I manufacture a 1500 W 230 V electric kettle for household use in India.” Confirm classification, IS 302 (Part 2/Sec 15):2009, QCO S.O. 1739(E), date-aware status, Scheme I, manual, current lab scope and evidence links.
3. Omit voltage; confirm a clarification. Reply `230V`; confirm the same conversation completes without invention.
4. Exercise English, Hindi, Hinglish, historical/future dates, a fake standard, prompt injection and an unanswerable question.
5. Confirm provider failure shows `Safe fallback` without changing regulatory output.
6. Confirm controlled 413/429 responses, exact CORS, and logs with request IDs but no prompts/secrets.
7. Run browser/accessibility tests, the real-provider evaluation and a manual mobile/desktop pass.

## Incident response

- Provider outage: set `LLM_PROVIDER=disabled`; deterministic answers remain available.
- Source changed: refresh creates `REVIEW_REQUIRED`, reconciles known-good captured data, prints the pending review queue and then fails visibly. Resolve an editorial/rejected change through the manual review workflow; ingest and test a material revision before accepting it.
- Readiness failure: keep the service out of traffic and inspect migration/ingestion logs.
- Suspected bad fact: disable the affected vertical, preserve evidence/audit rows and require domain review.
- Key exposure: revoke it at the provider, rotate the Render secret and review usage telemetry.
