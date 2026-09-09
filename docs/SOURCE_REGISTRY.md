# Source registry

`backend/app/data/source_registry.json` is the allow-listed catalogue of authorities, hosts, source types, adapter ownership, refresh cadence and content boundary. Phase 3B accepts BIS web and BIS LIMS sources. Runtime URL validation rejects non-HTTPS URLs, credentials in URLs and hosts outside the registry.

Discovery and verification are different:

- The Scheme I index and product-manual catalogue are useful for candidate discovery and cross-checking.
- Gazetted QCO documents verify notification identity, product schedule, scheme and implementation dates.
- Product manuals verify product-specific implementation metadata where the document or authoritative listing supports it.
- LIMS verifies laboratory recognition and scope only to the detail and validity date exposed by the stored source.

Discovery never auto-publishes compliance. Search-engine results and snippets may locate an official page but are not canonical records. Canonical records point to official BIS/government URLs and keep retrieval timestamps, hashes, identifiers and source status.

Rights remain a policy boundary. ManakAI stores metadata and limited retrieval text necessary for evidence navigation; it does not provide bulk downloads or recreate complete Indian Standards.
