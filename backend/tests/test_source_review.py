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


def test_repeated_unreviewed_source_changes_keep_one_actionable_item(db_session):
    event = _pending_change(db_session)
    pending_before = list(
        db_session.scalars(
            select(SourceChangeEvent).where(
                SourceChangeEvent.source_url == event.source_url,
                SourceChangeEvent.review_status == "PENDING",
            )
        )
    )
    first_new_hash = event.new_hash

    async def changed_again(url):
        return FetchedSource(url, b"review-changed-again", "text/html")

    asyncio.run(refresh_authoritative_sources(db_session, changed_again))
    pending_after = list(
        db_session.scalars(
            select(SourceChangeEvent).where(
                SourceChangeEvent.source_url == event.source_url,
                SourceChangeEvent.review_status == "PENDING",
            )
        )
    )
    assert len(pending_after) == len(pending_before) == 1
    assert pending_after[0].new_hash != first_new_hash


def test_review_report_collapses_legacy_duplicates_and_resolution_supersedes_them(db_session):
    event = _pending_change(db_session)
    duplicate = SourceChangeEvent(
        id="source-change-legacy-duplicate",
        source_url=event.source_url,
        source_type=event.source_type,
        previous_hash=event.previous_hash,
        new_hash="c" * 64,
        status="REVIEW_REQUIRED",
        change_classification="MATERIAL",
        review_status="PENDING",
        changed_fields=["source_fingerprint"],
    )
    db_session.add(duplicate)
    db_session.commit()

    report = review_report(db_session)
    item = next(item for item in report["pending_events"] if item["source_url"] == event.source_url)
    assert item["id"] == duplicate.id
    assert item["superseded_pending_event_ids"] == [event.id]

    resolve_review(
        db_session,
        event_id=duplicate.id,
        decision="ACCEPTED_EDITORIAL",
        expected_new_hash=duplicate.new_hash,
        reviewed_by="reviewer@example.test",
        review_note="The latest visible change is editorial.",
    )
    assert event.status == "RESOLVED"
    assert event.review_status == "SUPERSEDED"


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
    assert source.metadata_json["monitor_content_hash"] == event.new_hash
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
