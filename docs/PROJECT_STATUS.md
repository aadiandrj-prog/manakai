# Project status and roadmap

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

The model-provider fields and language properties are boundaries only. There is no production LLM adapter, evidence-only structured generation, prompt-injection defence, Hindi/Hinglish normalisation or multilingual evaluation. A future model may explain evidence, but must never set a regulatory fact.

### External-service workflows

The consumer screen does not verify HUIDs, complaints or licences. Authoritative mode contains two official LIMS scope snapshots; demo mode retains synthetic labs. Distance/geolocation, notifications, application submission, payments and document uploads are intentionally absent.

### Operations and hosting

The full stack needs a public FastAPI runtime and managed PostgreSQL/pgvector service, backups, point-in-time recovery, CI/CD migrations, metrics/traces, alerting, dependency scanning, accessibility/browser tests, load tests and disaster-recovery exercises. A frontend-only Sites deployment cannot provide the backend/database; `NEXT_PUBLIC_API_URL` must point at a separately deployed HTTPS API before the integrated frontend is redeployed publicly.

The current production npm audit reports six advisories (five high) in the Vinext/Vite/React Server Components/Undici toolchain. Several remediations require version changes outside the currently pinned ranges. Upgrade them on a dedicated compatibility branch, rerun browser and Docker tests, and do not release publicly while applicable high-severity findings remain.

## Constraints to preserve

- Never let browser code or an LLM determine legal/mandatory status.
- Never present demo, stale or inferred data as an official BIS record.
- Preserve source, version, location, effective date and retrieval time for important claims.
- Prefer current verified authoritative records and surface conflicts or missing evidence.
- Do not distribute protected standards content without permission.
- Keep demo mode deterministic, database-backed and usable without paid services.
- Keep the modular monolith until scale or isolation requirements justify more services.

## Recommended development sequence

1. Add scheduled live refresh, maker/checker review, staleness alerts and source-change diffs for the kettle adapters.
2. Obtain legal/rights review for retained excerpts and regulatory-domain review of the QCO/standard relationship.
3. Deploy FastAPI and managed PostgreSQL/pgvector behind HTTPS; configure CORS, secrets, backups and migration automation.
4. Upgrade the frontend dependency chain to resolve applicable high-severity advisories, then add browser, accessibility, security and load gates.
5. Provision the optional local embedding model in a controlled build step and evaluate hybrid retrieval against expert-labelled queries.
6. Pilot only this kettle vertical with a small manufacturer cohort and verify real application/laboratory interactions.
7. After the pilot, begin the separately scoped authentication/governance phase; do not widen product families first.

## Definition of the next milestone

The next milestone is an operationally governed kettle vertical: automated refresh, human approval, alerting, deployed full stack, dependency remediation and expert acceptance, while retaining deterministic decisions and the voltage/enterprise clarification boundary.
