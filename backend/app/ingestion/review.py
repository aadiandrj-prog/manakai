from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import db_models as m


REVIEW_DECISIONS = {"ACCEPTED_EDITORIAL", "ACCEPTED_MATERIAL", "REJECTED"}


def review_report(session: Session) -> dict:
    pending = list(
        session.scalars(
            select(m.SourceChangeEvent)
            .where(
                m.SourceChangeEvent.status == "REVIEW_REQUIRED",
                m.SourceChangeEvent.review_status == "PENDING",
            )
            .order_by(m.SourceChangeEvent.created_at.asc())
        )
    )
    latest_run = session.scalar(
        select(m.IngestionRun)
        .where(m.IngestionRun.adapter == "authoritative-source-refresh")
        .order_by(m.IngestionRun.started_at.desc())
        .limit(1)
    )
    return {
        "pending_count": len(pending),
        "pending_events": [
            {
                "id": event.id,
                "created_at": event.created_at.isoformat(),
                "source_url": event.source_url,
                "source_type": event.source_type,
                "change_classification": event.change_classification,
                "changed_fields": list(event.changed_fields or []),
                "material_summary": event.material_summary,
                "previous_hash": event.previous_hash,
                "new_hash": event.new_hash,
                "ingestion_run_id": event.ingestion_run_id,
                "affected_families": _affected_families(session, event.source_url),
            }
            for event in pending
        ],
        "latest_refresh": None
        if latest_run is None
        else {
            "run_id": latest_run.id,
            "started_at": latest_run.started_at.isoformat(),
            "finished_at": latest_run.finished_at.isoformat() if latest_run.finished_at else None,
            "status": latest_run.status,
            "records_fetched": latest_run.records_fetched,
            "records_rejected": latest_run.records_rejected,
            "errors": list(latest_run.errors or []),
        },
    }


def _affected_families(session: Session, source_url: str) -> list[dict]:
    rows = session.execute(
        select(m.ProductFamily.slug, m.ProductFamily.name, m.SourceFamilyImpact.impact_type)
        .join(m.SourceFamilyImpact, m.SourceFamilyImpact.product_family_id == m.ProductFamily.id)
        .join(m.SourceRecord, m.SourceRecord.id == m.SourceFamilyImpact.source_record_id)
        .where(m.SourceRecord.source_url == source_url)
        .distinct()
        .order_by(m.ProductFamily.slug, m.SourceFamilyImpact.impact_type)
    ).all()
    return [{"slug": slug, "name": name, "impact_type": impact_type} for slug, name, impact_type in rows]


def resolve_review(
    session: Session,
    *,
    event_id: str,
    decision: str,
    expected_new_hash: str,
    reviewed_by: str,
    review_note: str,
    canonical_content_hash: str | None = None,
) -> dict:
    if decision not in REVIEW_DECISIONS:
        raise ValueError(f"Unsupported review decision: {decision}")
    if not reviewed_by.strip() or not review_note.strip():
        raise ValueError("reviewed_by and review_note are required")
    event = session.get(m.SourceChangeEvent, event_id)
    if event is None:
        raise ValueError("Review event does not exist")
    if event.status != "REVIEW_REQUIRED" or event.review_status != "PENDING":
        raise ValueError("Review event is not pending")
    if event.new_hash != expected_new_hash:
        raise ValueError("The source changed again; expected_new_hash does not match the pending event")

    source = session.scalar(
        select(m.SourceRecord)
        .where(m.SourceRecord.source_url == event.source_url)
        .order_by(m.SourceRecord.retrieved_at.desc())
        .limit(1)
    )
    if source is None:
        raise ValueError("No canonical source record exists for this URL")

    if decision == "ACCEPTED_MATERIAL":
        if not canonical_content_hash or source.content_hash != canonical_content_hash:
            raise ValueError("ACCEPTED_MATERIAL requires the exact current canonical_content_hash")
        if source.retrieved_at <= event.created_at:
            raise ValueError("Material changes must be re-ingested after the review event before acceptance")

    # Editorial acceptance advances the relevant monitoring baseline without
    # altering canonical facts. Material acceptance is allowed only after a newer
    # canonical ingest. Rejection deliberately retains the old baseline.
    if decision in {"ACCEPTED_EDITORIAL", "ACCEPTED_MATERIAL"}:
        metadata = dict(source.metadata_json or {})
        if "source_fingerprint" in (event.changed_fields or []):
            metadata["monitor_content_hash"] = event.new_hash
            metadata["monitor_fingerprint_reviewed_at"] = datetime.now(timezone.utc).isoformat()
            metadata["monitor_stable_observations"] = 1
        else:
            metadata["raw_content_hash"] = event.new_hash
            metadata["raw_content_hash_reviewed_at"] = datetime.now(timezone.utc).isoformat()
        source.metadata_json = metadata

    event.status = "RESOLVED"
    event.review_status = decision
    event.reviewed_at = datetime.now(timezone.utc)
    event.reviewed_by = reviewed_by.strip()
    event.review_note = review_note.strip()
    event.canonical_source_record_id = source.id
    session.commit()
    return {
        "event_id": event.id,
        "status": event.status,
        "review_status": event.review_status,
        "source_url": event.source_url,
        "canonical_source_record_id": source.id,
    }
