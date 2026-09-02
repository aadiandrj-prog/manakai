# Data model

Phase 2C adds `conversations` and `conversation_messages`. A conversation stores detected language, current intent, structured product state, unresolved attributes, active compliance profile, relevant standard and evidence references. Messages store role, content, language and non-sensitive provider/fallback metadata. Neither table stores chain-of-thought.

The relational model is defined in `backend/app/db_models.py` and covers users, products, product profiles, standards, standard relationships, documents, chunks, QCOs, certification schemes, tests, laboratories, recognition scopes, product manuals, rules, compliance profiles, journeys and citations.

Standards form a relational graph through `standard_relationships`; supported relationship labels include `REFERENCES`, `SUPERSEDES`, `AMENDS`, `RELATED_TO`, `TESTED_USING`, `IMPLEMENTED_BY` and `REGULATED_BY`. Neo4j is unnecessary for the MVP.

Document chunks retain document ID, page, clause, section and text. The initial migration stores embeddings as `vector(384)` on PostgreSQL/pgvector and uses JSON only as a portable SQLite test fallback.

Temporal records store status, publication/effective dates, supersession links and retrieval timestamps. The rule engine must reject missing provenance and must never let an older superseded record silently override a current active record.

Fixture identifiers are for demo stability only and must not be reused as authoritative-source identifiers.

## Phase 2B entities

- `ingestion_runs`: adapter, timestamps, status and fetched/created/updated/rejected/error counters.
- `source_records`: URL, authority/type, temporal metadata, identifier, SHA-256 content hash and optional page/clause/table/gazette/standard fields.
- `provenance_links`: claim-level links from normalized records to source records.
- `product_categories` and `product_standard_mappings`: the sourced kettle/category/standard graph.
- `qco_applicability`: one row per QCO, enterprise category and covered product category; general, small and micro dates are not collapsed.

The 2025 household-appliances QCO is retained as `SUPERSEDED`; the 2026 QCO links both directions. Same-number standards may coexist as `DEMO` and `AUTHORITATIVE`, so uniqueness includes `source_kind`.

Documents add authority, verification, identifier, hash and temporal status. Chunks add heading, subclause, table, paragraph index and hash. Lab recognition adds scope, clause list, validity, state and LIMS source. Compliance profiles snapshot query date, mode and the explanation tree.

## Phase 2D telemetry

- `ai_usage_events`: provider/model, operation, status, latency, available token counts, correlation identifiers and answer-validation result. Prompt and answer bodies are deliberately excluded.
- `source_change_events`: source URL/type, previous/new hash, ingestion run and `REVIEW_REQUIRED` status. A change event never replaces or deletes canonical data automatically.
