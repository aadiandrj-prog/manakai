from dataclasses import replace
import asyncio

import pytest
from sqlalchemy import select, text

from app.config import settings, sqlalchemy_database_url
from app.db_models import SourceChangeEvent, SourceRecord
from app.evaluation.cases import CASES
from app.ingestion.base import FetchedSource, SOURCE_FINGERPRINT_VERSION, source_fingerprint
from app.ingestion.refresh import refresh_authoritative_sources
from app.middleware import StagingSafetyMiddleware
from app.services.ai_provider import AIProviderError, GeminiProvider, OpenAIProvider


def test_evaluation_dataset_is_bounded_and_covers_required_categories():
    assert 300 <= len(CASES) <= 450
    categories = {case.category for case in CASES}
    assert {"product_wording", "formats", "missing_information", "hinglish", "hindi", "adversarial", "temporal", "standards_qa"} <= categories
    assert {"phase_2e_helmet", "phase_2e_cement", "phase_2e_pressure-cooker", "phase_2e_hallmarking"} <= categories
    assert len({case.id for case in CASES}) == len(CASES)


def test_provider_model_allowlists_fail_closed():
    with pytest.raises(AIProviderError, match="ALLOWED"):
        OpenAIProvider(replace(settings, openai_api_key="test", llm_model="unapproved-model")).structured(system="x", user="{}", schema=type("Unused", (), {}))
    with pytest.raises(AIProviderError, match="ALLOWED"):
        GeminiProvider(replace(settings, gemini_api_key="test", llm_model="unapproved-model")).structured(system="x", user="{}", schema=type("Unused", (), {}))


def test_provider_postgres_urls_use_installed_psycopg_driver():
    expected = "postgresql+psycopg://user:secret@example.test/db"
    assert sqlalchemy_database_url("postgresql://user:secret@example.test/db") == expected
    assert sqlalchemy_database_url("postgres://user:secret@example.test/db") == expected


def test_rate_limiter_expires_old_requests():
    middleware = StagingSafetyMiddleware(lambda scope, receive, send: None, replace(settings, rate_limit_window_seconds=10))
    assert middleware._allowed(("127.0.0.1", "chat"), 2, 1) == (True, 0)
    assert middleware._allowed(("127.0.0.1", "chat"), 2, 2) == (True, 0)
    allowed, retry = middleware._allowed(("127.0.0.1", "chat"), 2, 3)
    assert allowed is False and retry == 8
    assert middleware._allowed(("127.0.0.1", "chat"), 2, 12) == (True, 0)


def test_request_size_limit_and_security_headers(client):
    too_large = client.post("/api/v1/chat", json={"query": "x" * 70000})
    assert too_large.status_code == 413
    response = client.get("/health", headers={"X-Request-ID": "known-request"})
    assert response.headers["x-request-id"] == "known-request"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_readiness_hides_database_error_details(client):
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "Service is not ready"}


def test_source_refresh_baselines_then_flags_change_without_overwriting(db_session):
    source = db_session.scalar(select(SourceRecord).where(SourceRecord.verification_status == "AUTHORITATIVE"))
    if source is None:
        from app.ingestion.pipeline import ingest_electric_kettle
        ingest_electric_kettle(db_session)
        source = db_session.scalar(select(SourceRecord).where(SourceRecord.verification_status == "AUTHORITATIVE"))
    original_hash = source.content_hash

    async def baseline(url):
        return FetchedSource(url, b"captured-v1", "text/html")

    first = asyncio.run(refresh_authoritative_sources(db_session, baseline))
    assert first["baselined"] > 0

    async def changed(url):
        return FetchedSource(url, b"captured-v2", "text/html")

    second = asyncio.run(refresh_authoritative_sources(db_session, changed))
    assert second["changes_review_required"] > 0
    assert db_session.get(SourceRecord, source.id).content_hash == original_hash
    assert db_session.scalar(select(SourceChangeEvent).where(SourceChangeEvent.status == "REVIEW_REQUIRED")) is not None


def test_html_fingerprint_ignores_scripts_attributes_and_formatting():
    first = FetchedSource(
        "https://www.bis.gov.in/example",
        b'<html><body><input value="csrf-one"><h1>IS 269</h1><script>nonce = "one"</script></body></html>',
        "text/html; charset=UTF-8",
    )
    second = FetchedSource(
        "https://www.bis.gov.in/example",
        b'<html>\n<body><input value="csrf-two"> <h1> IS 269 </h1><script>nonce = "two"</script></body></html>',
        "text/html",
    )
    changed = FetchedSource(
        "https://www.bis.gov.in/example",
        b"<html><body><h1>IS 269 withdrawn</h1></body></html>",
        "text/html",
    )

    assert source_fingerprint(first) == source_fingerprint(second)
    assert source_fingerprint(first) != source_fingerprint(changed)


def test_refresh_migrates_legacy_raw_hash_to_versioned_fingerprint(db_session):
    source = db_session.scalar(select(SourceRecord).where(SourceRecord.verification_status == "AUTHORITATIVE"))
    if source is None:
        from app.ingestion.pipeline import ingest_electric_kettle
        ingest_electric_kettle(db_session)
        source = db_session.scalar(select(SourceRecord).where(SourceRecord.verification_status == "AUTHORITATIVE"))
    source.metadata_json = {"raw_content_hash": "legacy-raw-hash"}
    db_session.commit()

    async def stable_html(url):
        return FetchedSource(url, b'<html><input value="changing-token"><p>Stable BIS record</p></html>', "text/html")

    first = asyncio.run(refresh_authoritative_sources(db_session, stable_html))
    second = asyncio.run(refresh_authoritative_sources(db_session, stable_html))

    assert first["baselined"] > 0
    assert second["changes_review_required"] == 0
    assert source.metadata_json["monitor_fingerprint_version"] == SOURCE_FINGERPRINT_VERSION
    assert source.metadata_json["monitor_stable_observations"] >= 2
