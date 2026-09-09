# Adding a product family

1. Add a declarative entry to `backend/app/data/product_families.json`. Include multilingual aliases, ambiguity terms, required/optional product attributes, product group and a conservative target coverage state.
2. Register only HTTPS sources accepted by `backend/app/data/source_registry.json`. Discovery indexes may identify candidates; a current standard, QCO, scheme, manual or laboratory claim must use verification evidence appropriate to that claim.
3. Stage one family without publishing it:

   ```bash
   cd backend
   python -m app.ingestion coverage-registry --family <slug> --dry-run
   python -m app.ingestion coverage-registry --family <slug>
   ```

4. Inspect normalized rows, provenance, version history, temporal dates, conflicts, score and the generated source-impact report. Add captured/sanitised fixtures and parameterized tests. Live BIS availability must not be required by tests.
5. Move `NEEDS_REVIEW → APPROVED` with a named reviewer, then publish in a separate action:

   ```bash
   python -m app.ingestion family-approve --family <slug> --reviewed-by "Reviewer name"
   python -m app.ingestion family-publish --family <slug>
   ```

Invalid state transitions fail. Ingestion cannot jump directly to public visibility. The bundled Phase 3B manifest is a special reviewed bootstrap dataset and uses `publish_reviewed=True` during deployment.

Do not mark a family `VERIFIED` merely because its standard appears on a BIS page. Verify the current version, product mapping, active instrument, enterprise dates, scheme, manual, source status and laboratory boundary. Where official pages disagree, keep every version and publish `PARTIAL` without an applicability edge.
