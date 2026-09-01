# Full-stack integration checklist

This phase preserves the current UI and replaces browser-local regulatory fixtures with the canonical request flow:

`Browser → Next.js/Vinext → FastAPI → service → repository → PostgreSQL`

## Fixture-to-endpoint replacement map

| Current frontend path | Existing local source | Canonical API replacement | Target state |
| --- | --- | --- | --- |
| `/` operational counts | Hard-coded standard/lab counts | `GET /api/v1/standards` + `GET /api/v1/labs` | Query API and render loading/error-safe counts |
| `/product` candidate match, attributes and warnings | `lib/demo-data.ts` | `POST /api/v1/products/analyse` | Backend classifies, evaluates rules, persists and returns `ComplianceProfile` |
| `/compliance/[id]` profile, tests, documents, journey and evidence | `emergencyProfile` + `journeySteps` | `GET /api/v1/compliance/{id}` + `GET /api/v1/compliance/{id}/journey` | Render backend-owned result only |
| `/standards` list and category filter | `standards` | `GET /api/v1/standards` / `POST /api/v1/standards/search` | Query repository-backed records |
| `/standards/[id]` standard and lab relationships | `standards` + `laboratories` | `GET /api/v1/standards/{id}` + `GET /api/v1/standards/{id}/relationships` | Render standard and typed relationships from API |
| `/labs` lab records and standard options | `laboratories` + `standards` | `GET /api/v1/labs` / `POST /api/v1/labs/search` | Server-side structured filtering |
| `/ask` seeded evidence answer | Hard-coded response cards | `POST /api/v1/qa` | Render backend answer, citations, confidence and warnings |
| `/consumer` explanatory HUID workflow | UI-only static guidance | No regulatory fixture dependency | Keep static until an authorised consumer-service API exists |
| `/about` architecture narrative | UI-only static content | No data endpoint required | Update wording after integration |

## Backend activation

- [x] Add SQLAlchemy engine/session lifecycle and database health check.
- [x] Add Alembic configuration and an initial PostgreSQL/pgvector migration.
- [x] Add idempotent demo and test seed commands.
- [x] Move canonical demo entities into backend seed definitions.
- [x] Add repositories for standards, labs, QCOs, products, documents and compliance profiles.
- [x] Refactor services to accept repositories/sessions instead of module fixtures.
- [x] Complete standard relationships and document endpoints.
- [x] Keep ORM entities behind Pydantic response schemas.

## Frontend integration

- [x] Add a generated OpenAPI type artifact and typed API client.
- [x] Add TanStack Query provider and feature hooks.
- [x] Replace every `lib/demo-data.ts` import.
- [x] Preserve existing layout and visual styling.
- [x] Add loading, empty, validation, backend and network-failure states.
- [x] Remove obsolete regulatory fixture duplication.

## Verification

- [x] Test migrations and seeds against PostgreSQL.
- [x] Test repositories/services against an isolated test database.
- [x] Verify every major API contract and generated OpenAPI schema.
- [x] Prove the frontend contains no regulatory fixture imports.
- [x] Verify Docker Compose startup, health and frontend-to-API communication.
- [x] Update README, architecture and project status documentation.
