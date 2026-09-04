# Authoritative BIS coverage

## Phase 2E coverage registry

The original kettle evidence remains unchanged. Phase 2E adds captured official BIS/government metadata for four more domains:

| Product/regime | Primary standard | Coverage | Integrated official evidence |
| --- | --- | --- | --- |
| Motorcycle helmets | IS 4151:2015 | VERIFIED | BIS standard page, Scheme I/QCO listing, PM/IS 4151/3/Dec 2024, two dated LIMS scopes |
| Ordinary Portland Cement | IS 269:2015 | VERIFIED | BIS standard page, Cement QCO/Scheme I listing, PM/IS 269/3/Oct 2023, grade-specific LIMS scopes |
| Domestic pressure cookers | IS 2347:2023 | PARTIAL | 2020 QCO, current and historical product manuals, current LIMS scope; Scheme I page revision mismatch and missing lab validity are warnings |
| Gold jewellery/hallmarking | IS 1417:2016 | PARTIAL | 2020/2021/2023/2026 order history, BIS hallmark/HUID/consumer guidance; live HUID verification and complete AHC directory are not ingested |

The captured multi-vertical fixture is `backend/tests/fixtures/official/multi_vertical.json`. It stores metadata and short operational summaries, not full Indian Standards. `AUTHORITATIVE` describes provenance from the linked official source, not a legal approval by ManakAI.

The HUID boundary is strict: ManakAI can explain the three hallmark elements and the official process, but a HUID is verified only through the BIS Care app. AHCs have a dedicated data model and are not mislabeled as ordinary BIS testing laboratories.

## Scope and capture

This section documents the original household-electric-kettle capture as appliances for heating liquids. The committed sanitised source fixture was captured on 2 September 2026. `AUTHORITATIVE` means the stored fact came directly from the linked BIS/government source; it does not mean ManakAI has performed legal certification or that the snapshot stays current forever.

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
python -m app.ingestion helmets
python -m app.ingestion cement
python -m app.ingestion pressure-cookers
python -m app.ingestion hallmarking
python -m app.ingestion all-authoritative
python -m app.ingestion embeddings --allow-model-download
python -m app.ingestion refresh
```

Each Phase 2E target stages and commits its own graph. `all-authoritative` reports per-vertical success/error results so a failed source does not erase or block unrelated known-good verticals.

## Metadata versus text

Complete Indian Standard text is not committed. The app stores standard title/number/year/status metadata, official links, QCO metadata and a small set of product-manual/QCO/LIMS excerpts needed to test clause retrieval and prove displayed claims. The UI does not offer bulk document download or reconstruct a standard.

## Rights and policy boundary

Public availability is not treated as permission for unrestricted redistribution. The current implementation assumes official metadata and narrowly necessary technical excerpts can be retained for this development prototype, but this has not received a formal copyright/licensing opinion. Before public commercial release, obtain legal review, document source-specific retention rights, and switch any disputed adapter to metadata-only mode. This is a design constraint, not a legal conclusion.

## Known limitations

- The snapshot is not a substitute for checking current Gazette/BIS/LIMS records.
- The exact voltage was absent from the example, so the QCO’s voltage scope is unresolved.
- Kettle implementation categories model `GENERAL`, `SMALL` and `MICRO`; other captured QCOs currently use the general applicability row. Exemptions, district coverage, turnover thresholds and stock-transition facts are not fully automated eligibility decisions.
- Lab addresses/scope are stored only where the official page exposed them; missing data is not inferred.
- The staging workflow schedules byte-level source checks and material-change classification, but maker/checker approval, notifications and semantic diff review remain manual.
- Complete AHC coverage, live HUID verification, full laboratory pagination and source-specific redistribution rights remain unresolved.
