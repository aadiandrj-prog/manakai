from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import select

from app.db_models import SourceChangeEvent, SourceRecord
from app.ingestion.base import FetchedSource
from app.ingestion.pipeline import ingest_electric_kettle
from app.ingestion.refresh import refresh_authoritative_sources
from app.ingestion.review import resolve_review, review_report


def _pending_change(db_session):
    ingest_electric_kettle(db_session)

    async def baseline(url):
        return FetchedSource(url, b"review-baseline", "text/html")

    async def changed(url):
        return FetchedSource(url, b"review-changed", "text/html")

    asyncio.run(refresh_authoritative_sources(db_session, baseline))
    asyncio.run(refresh_authoritative_sources(db_session, changed))
    return db_session.scalar(
        select(SourceChangeEvent)
        .where(SourceChangeEvent.review_status == "PENDING")
        .order_by(SourceChangeEvent.created_at.asc())
    )


def test_review_report_includes_pending_events_and_latest_fetch_errors(db_session):
    event = _pending_change(db_session)
    report = review_report(db_session)
    assert report["pending_count"] > 0
    assert report["pending_events"][0]["id"] == event.id
    assert report["pending_events"][0]["source_url"].startswith("https://")
    assert report["latest_refresh"]["status"] == "SUCCESS"


def test_editorial_resolution_is_audited_and_advances_only_raw_baseline(db_session):
    event = _pending_change(db_session)
    pending_before = review_report(db_session)["pending_count"]
    source = db_session.scalar(
        select(SourceRecord)
        .where(SourceRecord.source_url == event.source_url)
        .order_by(SourceRecord.retrieved_at.desc())
    )
    canonical_hash = source.content_hash

    result = resolve_review(
        db_session,
        event_id=event.id,
        decision="ACCEPTED_EDITORIAL",
        expected_new_hash=event.new_hash,
        reviewed_by="reviewer@example.test",
        review_note="The official regulatory fields are unchanged; only page presentation changed.",
    )

    assert result["review_status"] == "ACCEPTED_EDITORIAL"
    assert source.content_hash == canonical_hash
    assert source.metadata_json["raw_content_hash"] == event.new_hash
    assert event.status == "RESOLVED"
    assert event.reviewed_at is not None
    assert event.reviewed_by == "reviewer@example.test"
    assert review_report(db_session)["pending_count"] == pending_before - 1


def test_review_resolution_rejects_stale_or_unsafe_material_acceptance(db_session):
    event = _pending_change(db_session)
    with pytest.raises(ValueError, match="changed again"):
        resolve_review(
            db_session,
            event_id=event.id,
            decision="REJECTED",
            expected_new_hash="0" * 64,
            reviewed_by="reviewer",
            review_note="Reviewed",
        )
    with pytest.raises(ValueError, match="canonical_content_hash"):
        resolve_review(
            db_session,
            event_id=event.id,
            decision="ACCEPTED_MATERIAL",
            expected_new_hash=event.new_hash,
            reviewed_by="reviewer",
            review_note="Material update",
        )
