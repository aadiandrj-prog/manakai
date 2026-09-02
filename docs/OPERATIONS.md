# Operations

FastAPI logs request ID, route, status and latency. AI calls persist provider, model, operation, latency, available token counts, status and answer-validation result. Source-change rows capture hashes requiring human review. Secrets, prompts and generated answers are excluded from operational logs.

Minimum staging alerts are repeated `/ready` failure, 5xx rate, ingestion failure, source changes awaiting review, abnormal daily AI usage, provider fallback rate and database pressure. Centralized metrics/traces and paging remain external deployment work.

Resource/cost controls include a single small API instance, bounded request/prompt/evidence/output/history sizes, model allow-lists, short timeout, one retry, database-counted daily provider cap, exact CORS and deterministic fallback. The in-memory anonymous limiter is only valid for one instance; use a shared limiter before horizontal scaling.

## Dependency review

On 2 September 2026, `npm audit` initially reported 11 findings. React/RSC moved to 19.2.8, Vinext to beta.8, Vite to 8.2.2 and matching Cloudflare/RSC/Wrangler packages to patched versions. Tests/build passed and a repeat audit reported zero known vulnerabilities. CI now rejects high-severity advisories. This is point-in-time evidence, not continuous assurance.
