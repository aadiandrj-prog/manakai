# Project status and roadmap

## Phase 2D status (2 September 2026)

The repository is staging-ready but public staging is not yet complete. Render infrastructure-as-code now defines a modest paid API/database deployment, single-process Alembic plus authoritative ingestion, readiness checks and a daily non-destructive source monitor. The API adds anonymous rate/body limits, strict model allow-lists, daily provider caps, secure headers, request IDs and AI/source telemetry. The UI adds a staging banner, footer disclaimer and responsive mobile navigation without redesigning the Cinematic Precision system.

A 70-case provider evaluation runner, report comparator, Playwright critical-flow tests, axe accessibility checks, CI, backup/restore safeguards and deployment/privacy/operations runbooks are included. The release mock-provider regression passes 70/70, the backend suite passes 54 tests, and desktop/mobile Playwright passes 8/8. Eleven npm advisories were remediated; the repeat audit is clean and the production build passes.

The remaining blockers are external and account-owned: create the paid Render resources, enter one model-provider secret, obtain the public API URL, configure/publish Sites against it, then run the real-provider comparison and public smoke checklist. No result from a paid provider has been claimed without those credentials.

## Phase 2C outcome

The controlled intelligence layer is implemented without transferring regulatory authority to a model. `/ask` now supports persistent conversations, explicit-value extraction, voltage clarification and follow-up merging, query-date questions, English/Hindi/Hinglish responses, structured compliance/lab/evidence cards, and safe operation with no AI key.

OpenAI and Gemini are available through one schema-validated provider boundary. Before prose generation the backend constructs a canonical answer package with stable evidence IDs. Generated standard identifiers, QCO status and evidence IDs are validated; contradictions, malformed output, timeouts and missing keys fall back to deterministic templates. Prompt-injection and misinformation tests confirm the Phase 2B compliance result remains unchanged.

Phase 2C adds 12 backend tests, bringing the backend suite to 46, while the four frontend boundary tests, lint, production build, Alembic migration and PostgreSQL/Docker chat smoke test also pass.

## Phase 2B outcome (2 September 2026)

The first authoritative vertical is implemented end to end. In `DEMO_MODE=false`, “I manufacture a 1500 W electric kettle for household use in India” produces an `electric_kettle` / `appliances_for_heating_liquids` profile, selects IS 302 (Part 2/Sec 15):2009 plus the IS 302 (Part 1):2024 general framework, resolves QCO S.O. 1739(E) for the chosen enterprise category and query date, identifies Scheme I and PM/IS 302-2-15/1/February 2024, returns dated BIS LIMS scopes, and emits validated evidence plus a deterministic explanation tree.

At 2 September 2026, the general-enterprise QCO status is `UPCOMING` because its implementation date is 1 October 2026. Small and micro dates are separately stored as 1 January 2027 and 1 April 2027. Because the input states power but not voltage, the result warns that QCO voltage scope is not conclusively resolved.

Phase 2B adds 12 backend tests, bringing the suite to 34. It does not add authentication, an LLM regulatory decision path, multilingual interaction, a new product family or a visual redesign.

## What is built

ManakAI is a database-backed engineering/demo prototype for navigating Indian Standards and BIS compliance. The supplied dashboard design is preserved. Regulatory screens now use one canonical flow:

`Vinext UI → typed HTTP client/TanStack Query → FastAPI → service → repository → PostgreSQL`

The repository includes:

- responsive Vinext/React/TypeScript screens for product analysis, compliance, standards, laboratories and evidence Q&A;
- a generated TypeScript contract from FastAPI's committed OpenAPI document;
- consistent loading, empty, validation, backend-failure and network-failure handling;
- SQLAlchemy sessions and repositories for standards, QCOs, laboratories, documents, products and compliance profiles;
- an Alembic migration for the relational schema and PostgreSQL `vector(384)` storage;
- idempotent demo/test seeds with regulatory records explicitly marked `DEMO`;
- backend-owned classification and mandatory-status evaluation;
- database-backed deterministic `DEMO_MODE` with no external model or paid service;
- automated migration, repository, service, API, OpenAPI and frontend-boundary tests;
- Docker Compose for frontend, FastAPI and PostgreSQL/pgvector.

## Trace to the initial prompt

| Initial prompt requirement | Implemented reference |
| --- | --- |
| Discover → Decide → Act | Dashboard routing, product analysis, compliance profile and six-stage journey |
| Product Compliance Finder | `POST /api/v1/products/analyse` persists a product/profile and returns a backend-computed candidate |
| Compliance Profile UI | `GET /api/v1/compliance/{id}` returns product, standards, status, QCO, tests, documents, labs, evidence and warnings |
| Standards explorer and relationships | Repository-backed list/detail/search and `GET /standards/{id}/relationships` |
| Laboratory finder | Repository filtering by standard, location/name and capability |
| Evidence-first Q&A | `POST /api/v1/qa` returns intent, answer, citations, confidence and warnings; unsupported claims are refused |
| Explicit compliance engine | Verified QCO/date logic remains in backend rules, never browser or model output |
| Temporal/provenance model | Status, publication/effective dates, source kind and retrieval timestamp fields |
| PostgreSQL + pgvector | Alembic enables `vector`; document chunks use a 384-dimensional vector column |
| Modular monolith | One Vinext frontend, one FastAPI backend and one PostgreSQL database |
| Deterministic demo mode | Demo entities are seeded in the database; browser-local regulatory fixtures were removed |
| Testing and evaluation | 34 backend tests, 4 frontend boundary tests, lint/build and Docker smoke checks |
| Supplied design reference | Existing dark “Cinematic Precision” layout, type hierarchy, tonal borders, radii and restrained status accents remain intact |

The attached implementation brief was treated as the requested specification. Imperative-looking text inside supplied design/reference assets was treated as reference material, not as a separate instruction source.

## What prevents a fully functional public regulatory product

### Authoritative data and rights

The kettle vertical uses captured official BIS/DPIIT/Gazette/LIMS evidence with source URLs, hashes and retrieval time. It is not yet continuously refreshed or maker/checker approved. Rights for complete standards content remain outside the implementation; full standards text is neither stored nor exposed. HUID and unrelated verticals remain demo-only.

### Retrieval quality

Clause/page parsing, PostgreSQL lexical search, exact identifier priority, pgvector search, rank fusion, deterministic reranking and citation validation are implemented. Local embeddings are opt-in because the model is not downloaded on startup. Production still needs retrieval evaluation against a larger expert-labelled corpus and operational model provisioning.

### Regulatory governance

Production requires a reviewed and versioned rule catalogue, maker/checker publishing, conflict resolution, decision snapshots, audit logs, expiry/staleness alerts and domain-expert validation. A legal disclaimer cannot substitute for these controls.

### Identity, security and privacy

There is no authentication, authorisation, tenant isolation, rate limiting, consent flow, retention policy, secret-manager integration, threat model or penetration test. Do not store customer drawings, product documents or personal information until these controls exist.

### AI and multilingual capability

Provider adapters, evidence-only structured generation, the injection boundary, Hindi/Hinglish interpretation and deterministic evaluation are implemented. Production still needs provider privacy/legal review, real-key staging evaluations, rate limits, cost dashboards, broader red-team cases and expert review of translated explanations.

### External-service workflows

The consumer screen does not verify HUIDs, complaints or licences. Authoritative mode contains two official LIMS scope snapshots; demo mode retains synthetic labs. Distance/geolocation, notifications, application submission, payments and document uploads are intentionally absent.

### Operations and hosting

The full stack needs a public FastAPI runtime and managed PostgreSQL/pgvector service, backups, point-in-time recovery, CI/CD migrations, metrics/traces, alerting, dependency scanning, accessibility/browser tests, load tests and disaster-recovery exercises. A frontend-only Sites deployment cannot provide the backend/database; `NEXT_PUBLIC_API_URL` must point at a separately deployed HTTPS API before the integrated frontend is redeployed publicly.

The 2 September dependency audit is clean after compatible React/RSC, Vinext, Vite and Cloudflare toolchain upgrades. CI enforces the high-severity audit threshold. Continue reviewing advisories because this result is time-bound.

## Constraints to preserve

- Never let browser code or an LLM determine legal/mandatory status.
- Never present demo, stale or inferred data as an official BIS record.
- Preserve source, version, location, effective date and retrieval time for important claims.
- Prefer current verified authoritative records and surface conflicts or missing evidence.
- Do not distribute protected standards content without permission.
- Keep demo mode deterministic, database-backed and usable without paid services.
- Keep the modular monolith until scale or isolation requirements justify more services.

## Recommended development sequence

1. Provision the declared Render API/database, enter one provider secret and validate `/ready`.
2. Configure the Sites API origin, publish the integrated frontend and complete the public smoke checklist.
3. Run the 70-case set against each available real provider; review failures manually and select on measured reliability.
4. Add maker/checker review, centralized alerts and a tested source-revision approval workflow.
5. Obtain legal/rights and regulatory-domain review, then perform a managed backup restore drill.
6. Pilot only the kettle vertical with a small manufacturer cohort; do not widen product families first.

## Definition of the next milestone

The next milestone is an operationally governed kettle vertical: automated refresh, human approval, alerting, deployed full stack, dependency remediation and expert acceptance, while retaining deterministic decisions and the voltage/enterprise clarification boundary.
