# Published coverage

Phase 3B publishes 20 product families from the reviewed declarative registry in `backend/app/data/product_families.json`. Thirteen are `VERIFIED`; seven are deliberately `PARTIAL`. These labels describe ManakAI's evidence completeness, not a certification decision about a particular product.

## Verified families

Electric kettles, motorcycle helmets, Ordinary Portland Cement, electric ceiling fans, electrical appliance fans, electric irons, electric immersion water heaters, room heaters, toasters/grills/roasters, range hoods, skin/hair-care appliances, stationary storage water heaters and instantaneous electric water heaters.

## Partial families

Domestic pressure cookers, gold jewellery/hallmarking, self-ballasted LED lamps, plywood for general purposes, domestic LPG stoves, safety glass and plugs/socket-outlets.

Partial means at least one current-version, QCO/amendment, subtype, manual, laboratory-validity or official-service boundary remains unresolved. The application displays the exact limitation and does not silently promote metadata to applicability.

The plywood regression is intentional: the current BIS manual listing identifies IS 303:2024 while the captured 2024 QCO schedule identifies IS 303:1989. Both versions are preserved, the old one points to the new one, and the product remains `PARTIAL` with no published mandatory-status conclusion until the transition has authoritative support.

## Completeness dimensions

Internal scoring checks classification aliases, primary standard, version status, regulatory regime, temporal dates, certification scheme, product manual, laboratory relationship, citations and freshness review. A numeric score is diagnostic only; it cannot publish a family or override a human decision.

Laboratory completeness is separate. `COMPLETE`, `SOURCE_SCOPED`, `DIRECTORY_QUERY`, `METADATA_ONLY` and `CONFLICT_REVIEW` describe what the stored LIMS evidence can support. A query link is not a claim that a particular laboratory is currently recognised.

## Public contract

Only `PUBLISHED` coverage appears at `/api/v1/coverage`, `/api/v1/coverage/suggestions` and the `/coverage` page. Unsupported descriptions can show related standards metadata, but it is visibly labelled “not an applicability decision.”
