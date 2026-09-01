# Authoritative kettle data

## Scope and capture

This integration covers only household electric kettles as appliances for heating liquids. The committed sanitised source fixture was captured on 2 September 2026. `AUTHORITATIVE` means the stored fact came directly from the linked BIS/government source; it does not mean ManakAI has performed legal certification or that the snapshot stays current forever.

## Official sources integrated

| Source | Stored content | Canonical facts |
| --- | --- | --- |
| [BIS safety guide](https://www.services.bis.gov.in/tmp/tbl5_2024-11-11_1130.pdf) | Metadata and short classification excerpt | Electric kettles are examples of appliances for heating liquids; IS 302-2-15 is the product-specific safety standard |
| [BIS product manual](https://www.bis.gov.in/wp-content/uploads/2024/03/PM_302-2-15.pdf) | Manual metadata and limited clause-aware operational excerpts | PM/IS 302-2-15/1/February 2024; IS 302-2-15:2009; sampling/grouping declarations and cordless-kettle sampling |
| [2026 QCO / Gazette](https://www.bis.gov.in/wp-content/uploads/2026/04/Safety-of-Household-Commercial-and-Similar-Electrical-Appliances-Quality-Control-Order-2026.pdf) | Notification metadata and scope/date/scheme excerpt | S.O. 1739(E); supersedes 2025 Order; Appliances for Heating Liquids; IS 302 Part 1:2024; Scheme I; 1 Oct 2026 / 1 Jan 2027 / 1 Apr 2027 dates |
| [BIS Scheme I list](https://www.bis.gov.in/product-certification/products-under-compulsory-certification/scheme-i-mark-scheme/?lang=en) | List metadata | The QCO family and Appliances for Heating Liquids appear under Scheme I |
| [Shri Krishna Test House LIMS scope](https://lims.bis.gov.in/home_lab_scope/93/?page=2) | Lab identity/address, standard scope, clauses and validity | Scope for IS 302 Part 2/Sec 15:2009; validity 5 Oct 2028 |
| [MSME Testing Centre LIMS scope](https://lims.bis.gov.in/home/search_is_number/?is_number_doc_no=18112&lab_lab_nameicontains=&page=1&page=2&page=472&page=473) | Lab/OSL metadata, standard scope, exclusions and validity | OSL 8101204; validity 31 Dec 2026; EMI/EMC clauses 19.11.4.1–19.11.4.7 excluded |

The ingested testing list is a conservative subset of headings visible in official LIMS scopes: marking/instructions, power input/current, heating, leakage current/electric strength, moisture resistance, abnormal operation, mechanical strength, and resistance to heat/fire. It is not represented as a substitute for the complete standard or a laboratory quotation.

## Refresh and failure behaviour

Each adapter normalizes independently but the vertical commits atomically. An ingestion run records counts/errors. Source content receives a stable SHA-256 hash; unchanged records are reused, changed content creates a new source record, and prior regulatory history remains. Parse/validation failures roll back staged changes. An absent listing is treated as potential staleness/review, never automatic deletion.

Development commands:

```bash
python -m app.ingestion standards --dry-run
python -m app.ingestion qco --dry-run
python -m app.ingestion labs --dry-run
python -m app.ingestion electric-kettle
python -m app.ingestion embeddings --allow-model-download
```

The three sub-target commands currently validate and ingest the same atomic kettle graph so they cannot expose a partially connected regulatory state.

## Metadata versus text

Complete Indian Standard text is not committed. The app stores standard title/number/year/status metadata, official links, QCO metadata and a small set of product-manual/QCO/LIMS excerpts needed to test clause retrieval and prove displayed claims. The UI does not offer bulk document download or reconstruct a standard.

## Rights and policy boundary

Public availability is not treated as permission for unrestricted redistribution. The current implementation assumes official metadata and narrowly necessary technical excerpts can be retained for this development prototype, but this has not received a formal copyright/licensing opinion. Before public commercial release, obtain legal review, document source-specific retention rights, and switch any disputed adapter to metadata-only mode. This is a design constraint, not a legal conclusion.

## Known limitations

- The snapshot is not a substitute for checking current Gazette/BIS/LIMS records.
- The exact voltage was absent from the example, so the QCO’s voltage scope is unresolved.
- Only `GENERAL`, `SMALL` and `MICRO` implementation categories are modeled; exemptions and stock-transition facts are retained in evidence but not automated as eligibility decisions.
- Lab addresses/scope are stored only where the official page exposed them; missing data is not inferred.
- Live refresh scheduling, maker/checker approval, notifications and diff review are not deployed.
