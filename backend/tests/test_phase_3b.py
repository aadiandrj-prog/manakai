from dataclasses import replace
from datetime import date

import pytest
from sqlalchemy import select

from app import db_models as m
from app.coverage_onboarding import coverage_score, ingest_family_registry, transition_family
from app.coverage_registry import classify_from_registry, load_family_registry
from app.evaluation.cases import CASES
from app.ingestion.review import review_report
from app.ingestion.verticals import ingest_all_authoritative
from app.repositories import CoverageRepository
from app.schemas import ProductAnalyseRequest
from app.services import compliance as compliance_module
from app.services.compliance import ComplianceService
from app.source_registry import validate_official_source_url


@pytest.fixture()
def phase3b(db_session, monkeypatch):
    result = ingest_all_authoritative(db_session)
    assert result["status"] == "SUCCESS", result
    monkeypatch.setattr(compliance_module, "settings", replace(compliance_module.settings, demo_mode=False))
    return db_session


def test_registry_has_reviewed_scale_and_scoring():
    families = load_family_registry()
    assert len(families) == 20
    assert sum(item["coverage_status"] == "VERIFIED" for item in families) == 13
    assert sum(item["coverage_status"] == "PARTIAL" for item in families) == 7
    assert all(coverage_score(item)["total"] == 10 for item in families)
    assert all(coverage_score(item)["score"] == 100 for item in families if item["coverage_status"] == "VERIFIED")


def test_every_declared_source_is_in_the_official_source_registry():
    for family in load_family_registry():
        urls = [family.get("standard_source"), family.get("lims_url"), (family.get("qco") or {}).get("url"), (family.get("manual") or {}).get("url")]
        for url in filter(None, urls):
            validate_official_source_url(url)


@pytest.mark.parametrize("family", load_family_registry(), ids=lambda item: item["slug"])
def test_each_family_primary_alias_is_classified(family):
    result = classify_from_registry(f"I manufacture {family['aliases'][0]} in India")
    assert result["category_slug"] == family["slug"]
    assert result["structured"]["product_type"] == family["product_type"]


@pytest.mark.parametrize("query", ["I make a fan", "I make a heater", "I make a helmet", "I sell glass"])
def test_cross_family_terms_request_clarification(query):
    result = classify_from_registry(query)
    assert result.get("ambiguous") is True
    assert len(result["structured"]["candidate_categories"]) >= 2


def test_only_reviewed_families_are_public(db_session):
    ingest_family_registry(db_session, publish_reviewed=False, only_slug="electric-ceiling-fan")
    assert CoverageRepository(db_session).for_category("electric-ceiling-fan") is None
    family = db_session.scalar(select(m.ProductFamily).where(m.ProductFamily.slug == "electric-ceiling-fan"))
    assert family.lifecycle_status == "NEEDS_REVIEW"
    transition_family(db_session, family.slug, "APPROVED", reviewer="test reviewer")
    transition_family(db_session, family.slug, "PUBLISHED")
    assert CoverageRepository(db_session).for_category(family.slug) is not None


def test_published_coverage_and_api_counts(phase3b, client):
    rows = CoverageRepository(phase3b).list()
    stats = client.get("/api/v1/coverage/stats").json()
    suggestions = client.get("/api/v1/coverage/suggestions?q=heater").json()
    assert len(rows) == stats["total"] == 20
    assert stats["verified"] == 13 and stats["partial"] == 7
    assert stats["current_standards"] == 20
    assert {item["slug"] for item in suggestions} >= {"room-heater", "electric-immersion-water-heater"}


@pytest.mark.parametrize("family", [item for item in load_family_registry() if item["coverage_status"] == "VERIFIED"], ids=lambda item: item["slug"])
def test_every_verified_family_has_a_resolved_graph(phase3b, family):
    profile = ComplianceService(phase3b).analyse(ProductAnalyseRequest(description=f"I manufacture {family['aliases'][0]} in India", as_of_date=date(2027, 5, 1)))
    assert profile.coverage.coverage_status.value == "VERIFIED"
    assert profile.applicable_standards
    assert profile.qco is not None
    assert profile.certification_scheme is not None
    assert profile.evidence


def test_ceiling_fan_temporal_status_is_date_aware(phase3b):
    service = ComplianceService(phase3b)
    before = service.analyse(ProductAnalyseRequest(description="electric ceiling fan", as_of_date=date(2023, 8, 1)))
    upcoming = service.analyse(ProductAnalyseRequest(description="electric ceiling fan", as_of_date=date(2023, 12, 1)))
    active = service.analyse(ProductAnalyseRequest(description="electric ceiling fan", as_of_date=date(2024, 2, 14)))
    assert before.qco is None and before.mandatory_status == "UNVERIFIED"
    assert upcoming.qco.status.value == "UPCOMING"
    assert active.qco.status.value == "ACTIVE"


def test_plywood_revision_conflict_does_not_become_applicability(phase3b):
    profile = ComplianceService(phase3b).analyse(ProductAnalyseRequest(description="general purpose plywood", as_of_date=date(2026, 9, 9)))
    assert profile.applicable_standards[0].version == "2024"
    assert profile.coverage.coverage_status.value == "PARTIAL"
    assert profile.qco is None
    assert profile.mandatory_status == "UNVERIFIED"
    old = phase3b.get(m.Standard, "is-303-1989-auth")
    assert old.status == "SUPERSEDED" and old.superseded_by_id == "is-303-2024-auth"


def test_source_impacts_and_refresh_groups_are_attributable(phase3b):
    impacts = list(phase3b.scalars(select(m.SourceFamilyImpact)))
    assert impacts
    ceiling = phase3b.scalar(select(m.ProductFamily).where(m.ProductFamily.slug == "electric-ceiling-fan"))
    assert {item.impact_type for item in impacts if item.product_family_id == ceiling.id} >= {"STANDARD_MAPPING", "REGULATORY_REQUIREMENT", "PRODUCT_MANUAL", "LABORATORY_SCOPE"}

    affected_existing = {
        slug
        for (slug,) in phase3b.execute(
            select(m.ProductFamily.slug)
            .join(m.SourceFamilyImpact, m.SourceFamilyImpact.product_family_id == m.ProductFamily.id)
            .join(m.SourceRecord, m.SourceRecord.id == m.SourceFamilyImpact.source_record_id)
            .where(
                m.SourceRecord.source_url.in_(
                    [
                        "https://lims.bis.gov.in/home/search_is_number/?is_number__doc_no=2347",
                        "https://lims.bis.gov.in/home/search_is_number/?is_number_doc_no=18112&lab_lab_nameicontains=&page=1&page=2&page=472&page=473",
                    ]
                )
            )
        )
    }
    assert affected_existing >= {"domestic-pressure-cooker", "appliances-for-heating-liquids"}


def test_existing_vertical_change_report_names_affected_family(phase3b):
    source_url = "https://lims.bis.gov.in/home/search_is_number/?is_number__doc_no=2347"
    phase3b.add(
        m.SourceChangeEvent(
            id="source-change-pressure-cooker-test",
            source_url=source_url,
            source_type="BIS_LIMS_SCOPE",
            previous_hash="a" * 64,
            new_hash="b" * 64,
            status="REVIEW_REQUIRED",
            change_classification="MATERIAL",
            review_status="PENDING",
            changed_fields=["source_fingerprint"],
        )
    )
    phase3b.commit()
    event = next(item for item in review_report(phase3b)["pending_events"] if item["id"] == "source-change-pressure-cooker-test")
    assert event["affected_families"] == [
        {
            "slug": "domestic-pressure-cooker",
            "name": "Domestic pressure cookers",
            "impact_type": "LABORATORY_SCOPE",
        }
    ]


def test_evaluation_corpus_exceeds_300_cases():
    assert len(CASES) >= 300
