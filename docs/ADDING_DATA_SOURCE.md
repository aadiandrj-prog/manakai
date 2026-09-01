# Adding an authoritative data source

1. Implement a source adapter with `fetch`, `parse`, `normalize` and `metadata` stages.
2. Preserve the source URL, publication/effective dates, retrieved timestamp, document version and checksum.
3. Store raw artefacts separately from normalised records.
4. Map standards and QCOs using stable source identifiers; never title text alone.
5. Validate status and supersession relationships before activating records.
6. Add fixture-backed contract tests for pagination, malformed documents and source outages.
7. Mark ingested records verified only after provenance and date fields pass validation.
8. Run the evaluation benchmark, especially citation correctness and version precedence.

Adapters must not bypass the repository or compliance-rule layers. Browser automation should be introduced only when an authoritative source genuinely requires it; normal HTTP and document parsers are preferred.
