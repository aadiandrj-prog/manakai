# Project status and roadmap

## What was built

ManakAI is a polished, deterministic Smart India Hackathon MVP for navigating Indian Standards and BIS compliance. It is deliberately structured as a compliance workspace rather than a generic chatbot.

The repository contains:

- a responsive React/Vinext/TypeScript frontend using Tailwind CSS and shadcn primitives;
- a modular FastAPI backend with typed request and response schemas;
- SQLAlchemy models for the proposed PostgreSQL/pgvector regulatory data model;
- deterministic product classification, intent routing, compliance-rule and retrieval services;
- clearly labelled fixture standards, laboratories, citations and three reliable demo journeys;
- Dockerfiles and Docker Compose for frontend, backend and PostgreSQL;
- automated route-contract, rule-engine, retrieval, intent, API and safety-boundary tests;
- architecture, data model, retrieval, compliance engine, demo and source-adapter documentation.

The hosted Sites deployment presents the frontend demo. The FastAPI and PostgreSQL services currently run locally or through Docker and are not part of that frontend-only hosting deployment.

## Trace to the original brief

| Original brief area | Implementation |
| --- | --- |
| Product philosophy: Discover → Decide → Act | Dashboard workflows, product analysis, compliance profile and action journey |
| “Do not build a generic chatbot” | Working-surface dashboard with six specialised workflows; Q&A is a secondary route |
| Product Compliance Finder | `/product` extracts a deterministic demo profile and candidate standard |
| Compliance Profile UI | `/compliance/demo-emergency-lamp` shows standards, status boundary, tests, documents, evidence, warnings and journey |
| Standards Q&A | `/ask` returns structured evidence cards and refuses unsupported clause claims |
| Standards explorer/detail | `/standards` and `/standards/[id]` expose version, status, scope and relationship metadata |
| Laboratory Finder | `/labs` filters structured synthetic lab records by location, standard and capability |
| Consumer Mode | `/consumer` provides HUID and certification-mark guidance separately from industry workflows |
| Evidence-first answers | Citation schemas, evidence register and explicit verified/demo/unverified source states |
| Temporal intelligence | Standard statuses, effective-date fields and tested version-precedence logic |
| Deterministic rule engine | Verified QCO/date evaluation is kept outside model output |
| Intent/orchestration layer | Serializable intent enum and deterministic fallback classifier |
| Modular backend/API | FastAPI routes for products, compliance, standards, labs, Q&A and citations |
| Structured database schema | SQLAlchemy models for the requested core tables and relational standard graph |
| Demo mode | No external model, database or network is required for the seeded scenarios |
| Development infrastructure | Frontend/backend Dockerfiles, PostgreSQL/pgvector Compose service and `.env.example` |
| Evaluation and testing | 19 backend tests, frontend route/safety contracts and a small deterministic benchmark |
| Documentation | README plus architecture, data, retrieval, compliance, demo and source-adapter guides |
| Supplied design reference | Deep-space surfaces, Manrope/Inter hierarchy, thin tonal borders, tight radii and restrained indigo/cyan status accents from “Cinematic Precision” |

## What is not production-ready

### 1. No authoritative BIS data integration

The standards, QCO, laboratory, product-manual and citation records are fixtures. Standard numbers and descriptions are demo metadata and are not continuously verified against official sources. Production use requires licensed/authorised sources, stable source identifiers, update schedules, checksums and provenance review.

### 2. The hosted frontend is not connected to the backend

Frontend scenarios currently use local TypeScript fixtures. The FastAPI service mirrors the domain flow, but the UI does not yet call it. A production deployment needs an API host, typed API client, loading/error/retry states and a single source of truth.

### 3. Persistence is modelled but not activated

SQLAlchemy tables exist, but there are no Alembic migrations, seeded PostgreSQL loader, pgvector extension migration or repository implementations. Compliance profiles and journey progress are stateless.

### 4. Retrieval is a deterministic prototype

The backend performs small keyword matching over fixtures. BM25, vector embeddings, fusion, reranking, structural document parsing, page/clause extraction and citation-span validation are not implemented.

### 5. Model providers are not wired

Environment fields exist for optional providers, but there is no provider adapter or structured-output call. Before enabling an LLM, add provider-neutral interfaces, Pydantic output validation, timeouts, cost controls, prompt-injection defences and evidence-only generation.

### 6. Regulatory and legal safeguards need formalisation

The prototype correctly withholds unverified mandatory-status claims, but production requires a reviewed rule catalogue, maker/checker publishing controls, versioned decisions, audit logs, conflict handling, legal disclaimers and domain-expert validation. Standards content may also be copyrighted or licensed; ingestion and display rights must be resolved.

### 7. Multilingual support is architectural only

The schema carries language fields and the UI signals English/Hindi intent, but there is no real language detection, canonical-query translation or Hindi/Hinglish response generation.

### 8. Consumer and laboratory integrations are guidance-only

HUID verification, complaint routing, BIS licence/mark checking, lab recognition status, distance and geolocation are not connected to official services. The app must not imply that it performed those checks.

### 9. Identity, security and privacy are intentionally minimal

There is no authentication, authorisation, tenant isolation, consent flow, rate limiting, secret manager, data-retention policy, security headers review, threat model or penetration test. These are mandatory before storing user/product documents or exposing provider-backed endpoints.

### 10. Production operations are incomplete

The project needs hosted API/database infrastructure, migrations, backups, health/readiness checks, structured traces and metrics, alerting, CI/CD, dependency scanning, accessibility testing, browser end-to-end tests, load testing and disaster-recovery procedures.

## Constraints to preserve

- Never let model output determine legal or mandatory status.
- Never present fixture, stale or inferred data as an official BIS record.
- Keep the exact source, version, page/clause, effective date and retrieval time for every important claim.
- Prefer the newest verified authoritative record and surface conflicts.
- Do not distribute protected standards text without permission.
- Keep demo mode deterministic and usable without external services.
- Continue using one modular backend and one primary relational database until scale proves otherwise.

## Recommended next steps

### Phase 1 — make the vertical slice real

1. Select one product vertical, ideally emergency luminaires or electric kettles.
2. Obtain authoritative standard metadata, QCO, product manual and lab-recognition sources with documented usage rights.
3. Implement source adapters and ingestion provenance.
4. Create Alembic migrations and PostgreSQL repository implementations.
5. Host FastAPI and PostgreSQL, then connect `/product` and `/compliance/[id]` to the API.
6. Add contract and end-to-end tests for that live vertical slice.

### Phase 2 — evidence retrieval and controlled AI

1. Parse authorised documents into clause/page-aware chunks.
2. Add PostgreSQL full-text search and pgvector embeddings.
3. Implement rank fusion, reranking and citation-span validation.
4. Add a provider abstraction with structured outputs and evidence-only prompts.
5. Build evaluation gates for citation correctness, version choice, clarification and hallucination rate.

### Phase 3 — production safeguards and broader workflows

1. Add authentication, roles, audit history and saved journeys.
2. Integrate verified lab, HUID/consumer and official BIS service links.
3. Implement English, Hindi and Hinglish query normalisation and responses.
4. Add CI/CD, security scanning, observability, accessibility and browser tests.
5. Run regulatory expert review and a pilot with manufacturers/consumers before public release.

## Definition of the next milestone

The next release should support one real product description end to end: persisted profile, authoritative candidate standard, verified current QCO decision, product manual, exact test scope, currently recognised laboratory results, evidence citations and a saved compliance journey—without relying on an LLM for any legal fact.
