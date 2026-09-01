# Data model

The relational model is defined in `backend/app/db_models.py` and covers users, products, product profiles, standards, standard relationships, documents, chunks, QCOs, certification schemes, tests, laboratories, recognition scopes, product manuals, rules, compliance profiles, journeys and citations.

Standards form a relational graph through `standard_relationships`; supported relationship labels include `REFERENCES`, `SUPERSEDES`, `AMENDS`, `RELATED_TO`, `TESTED_USING`, `IMPLEMENTED_BY` and `REGULATED_BY`. Neo4j is unnecessary for the MVP.

Document chunks retain document ID, page, clause, section and text. Retrieval vectors are logically separate; the placeholder JSONB field should become a pgvector `Vector` column in the first production migration.

Temporal records store status, publication/effective dates, supersession links and retrieval timestamps. The rule engine must reject missing provenance and must never let an older superseded record silently override a current active record.

Fixture identifiers are for demo stability only and must not be reused as authoritative-source identifiers.
