# Adding an authoritative data source

1. Implement `BISSourceAdapter` with separate `fetch`, `parse`, `normalize`, `validate` and `provenance` stages. Do not build a multi-source scraper.
2. Preserve the source URL, publication/effective dates, retrieved timestamp, document version and checksum. For scheduled monitoring, define a stable semantic fingerprint when the source contains dynamic markup.
3. Store raw artefacts separately from normalised records.
4. Map standards and QCOs using stable source identifiers; never title text alone.
5. Validate status and supersession relationships before activating records.
6. Add fixture-backed contract tests for pagination, malformed documents and source outages.
7. Mark ingested records verified only after provenance and date fields pass validation.
8. Run the evaluation benchmark, especially citation correctness and version precedence.

Adapters must not bypass the repository or compliance-rule layers. Browser automation should be introduced only when an authoritative source genuinely requires it; normal HTTP and document parsers are preferred.

Run `python -m app.ingestion <target> --dry-run` first. The pipeline validates, stages and commits only a consistent vertical. Failure marks the run failed and retains known-good data. Unchanged URL/hash pairs reuse source records; disappearance never deletes a regulation automatically.

Captured fixtures belong under `backend/tests/fixtures/official/` with the official URL and capture time. Retain only metadata/excerpts needed for tests, not complete protected standards.

For a new product family, follow [Adding a product family](ADDING_PRODUCT_FAMILY.md) and register the authority in [Source registry](SOURCE_REGISTRY.md). Do not add product-specific branches to the classifier, API or frontend. Reuse the adapter pipeline and declarative registry; add a source-specific adapter only when parsing semantics genuinely differ. Mark the record `PARTIAL` when QCO, current manual, lab validity or rights evidence is incomplete.

Current reproducible targets:

```bash
python -m app.ingestion helmets --dry-run
python -m app.ingestion cement --dry-run
python -m app.ingestion pressure-cookers --dry-run
python -m app.ingestion hallmarking --dry-run
python -m app.ingestion all-authoritative
python -m app.ingestion review-report --fail-on-pending
```
