# Coverage pipeline

The reusable flow is:

```text
source registry → discovery → adapter → normalized candidate → validation
→ NEEDS_REVIEW → human approval → PUBLISHED graph
→ repository/service/rules → FastAPI → frontend
```

`ProductFamily` stores aliases, required attributes, group, declarative config and lifecycle. `CoverageRecord` stores public evidence completeness, limitations, lab completeness, timestamps and reviewer attribution. `SourceFamilyImpact` answers which families may be affected when an official page changes.

Lifecycle states are `DISCOVERED`, `INGESTED`, `AUTO_VALIDATED`, `NEEDS_REVIEW`, `APPROVED`, `PUBLISHED` and `REJECTED`. Only approved records can be published. Automated scoring cannot approve a family.

Scheduled refresh is split by product group with bounded source counts and at most two concurrent jobs. Each URL is isolated: a timeout or parser failure is recorded without deleting known-good data or stopping unrelated groups. A final reconciliation reloads the reviewed manifest and the workflow fails if a human source review remains pending.

The review report resolves every monitored source through `SourceFamilyImpact`, including the five verticals that predate Phase 3B. Repeated observations of an unreviewed URL update one actionable item to the newest fingerprint; legacy duplicates remain auditable as superseded event IDs and are closed together when that source is reviewed.

The classifier selects the longest explicit alias and extracts only supplied attributes. Broad terms such as fan, heater, helmet and glass return candidates. The deterministic compliance engine then resolves stored relationships and QCO dates for the requested enterprise category and `as_of_date`; the optional language model only explains the resulting package.
