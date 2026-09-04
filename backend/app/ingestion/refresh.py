from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import db_models as m
from .adapters import BISStandardAdapter
from .base import SOURCE_FINGERPRINT_VERSION, source_fingerprint


async def refresh_authoritative_sources(session: Session, fetcher=None) -> dict:
    """Check stable live-source fingerprints; never rewrite canonical facts."""
    run = m.IngestionRun(id=str(uuid4()), adapter="authoritative-source-refresh", status="RUNNING", started_at=datetime.now(timezone.utc))
    session.add(run)
    session.commit()
    adapter = BISStandardAdapter()
    fetcher = fetcher or adapter.fetch
    sources = list(session.scalars(select(m.SourceRecord).where(m.SourceRecord.verification_status == "AUTHORITATIVE").order_by(m.SourceRecord.retrieved_at.desc())))
    latest_by_url = {}
    for source in sources:
        latest_by_url.setdefault(source.source_url, source)
    errors = []
    changes = baselined = 0
    for source in latest_by_url.values():
        try:
            fetched = await fetcher(source.source_url)
            metadata = dict(source.metadata_json or {})
            current_fingerprint = source_fingerprint(fetched)
            previous_fingerprint = metadata.get("monitor_content_hash")
            fingerprint_version = metadata.get("monitor_fingerprint_version")
            metadata["last_raw_content_hash"] = fetched.content_hash
            metadata["last_source_check_at"] = datetime.now(timezone.utc).isoformat()
            if fingerprint_version != SOURCE_FINGERPRINT_VERSION or not previous_fingerprint:
                metadata["monitor_fingerprint_version"] = SOURCE_FINGERPRINT_VERSION
                metadata["monitor_content_hash"] = current_fingerprint
                metadata["monitor_stable_observations"] = 1
                source.metadata_json = metadata
                baselined += 1
            elif previous_fingerprint != current_fingerprint:
                exists = session.scalar(select(m.SourceChangeEvent).where(
                    m.SourceChangeEvent.source_url == source.source_url,
                    m.SourceChangeEvent.previous_hash == previous_fingerprint,
                    m.SourceChangeEvent.new_hash == current_fingerprint,
                ))
                if not exists:
                    material_types = {"GOVERNMENT_QCO", "GOVERNMENT_HALLMARKING_ORDER", "BIS_PRODUCT_MANUAL", "BIS_STANDARD_METADATA", "BIS_LIMS_SCOPE"}
                    classification = "MATERIAL" if source.source_type in material_types else "EDITORIAL"
                    session.add(m.SourceChangeEvent(
                        id=f"source-change-{uuid4().hex}", source_url=source.source_url, source_type=source.source_type,
                        previous_hash=previous_fingerprint, new_hash=current_fingerprint, ingestion_run_id=run.id,
                        status="REVIEW_REQUIRED",
                        change_classification=classification, review_status="PENDING", changed_fields=["source_fingerprint"],
                        material_summary=f"{source.source_type} visible content changed; canonical records were retained pending review.",
                    ))
                    changes += 1
                source.metadata_json = metadata
            else:
                metadata["monitor_stable_observations"] = min(
                    int(metadata.get("monitor_stable_observations", 1)) + 1,
                    1_000_000,
                )
                source.metadata_json = metadata
        except Exception as exc:
            errors.append({"source_url": source.source_url, "error": type(exc).__name__})
    run.records_fetched = len(latest_by_url)
    run.records_updated = baselined
    run.records_rejected = len(errors)
    run.errors = errors
    run.finished_at = datetime.now(timezone.utc)
    run.status = "SUCCESS" if not errors else "PARTIAL" if len(errors) < len(latest_by_url) else "FAILED"
    session.commit()
    return {"run_id": run.id, "status": run.status, "sources_checked": len(latest_by_url), "baselined": baselined, "changes_review_required": changes, "errors": len(errors)}
