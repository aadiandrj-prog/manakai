from dataclasses import replace
from datetime import date

import pytest

from app.evaluation.cases import CASES
from app.ingestion.verticals import ingest_all_authoritative
from app.repositories import CoverageRepository
from app.schemas import ProductAnalyseRequest
from app.services import compliance as compliance_module
from app.services.compliance import ComplianceService
from app.services.product_catalog import classify_authoritative
from app.db_models import TestStandardRelationship as TestStandardRelationshipRecord
from sqlalchemy import select


@pytest.fixture()
def authoritative(db_session, monkeypatch):
    result = ingest_all_authoritative(db_session)
    assert result["status"] == "SUCCESS"
    monkeypatch.setattr(compliance_module, "settings", replace(compliance_module.settings, demo_mode=False))
    return db_session


@pytest.mark.parametrize(("description", "standard", "coverage", "regime"), [
    ("motorcycle helmet for a two-wheeler rider in India", "IS 4151", "VERIFIED", "PRODUCT_CERTIFICATION"),
    ("OPC 53 ordinary Portland cement in India", "IS 269", "VERIFIED", "PRODUCT_CERTIFICATION"),
    ("5 litre domestic pressure cooker in India", "IS 2347", "PARTIAL", "PRODUCT_CERTIFICATION"),
    ("22K916 gold jewellery with HUID", "IS 1417", "PARTIAL", "HALLMARKING"),
])
def test_authoritative_verticals_use_generic_graph(authoritative, description, standard, coverage, regime):
    profile = ComplianceService(authoritative).analyse(ProductAnalyseRequest(description=description, as_of_date=date(2026, 9, 4)))
    assert profile.applicable_standards[0].number == standard
    assert profile.coverage.coverage_status.value == coverage
    assert profile.regulatory_regime.regime_type.value == regime
    assert profile.evidence
    assert all(item.source_kind.value == "AUTHORITATIVE" for item in profile.evidence)


def test_ambiguous_helmet_and_unsupported_product_do_not_false_positive(authoritative):
    service = ComplianceService(authoritative)
    helmet = service.analyse(ProductAnalyseRequest(description="I manufacture a helmet"))
    fan = service.analyse(ProductAnalyseRequest(description="I manufacture a ceiling fan"))
    assert helmet.coverage.coverage_status.value == "UNSUPPORTED"
    assert helmet.applicable_standards == []
    assert "motorcycle-helmet" in " ".join(helmet.warnings)
    assert fan.coverage.coverage_status.value == "UNSUPPORTED"
    assert fan.applicable_standards == []


def test_pressure_cooker_revision_history_and_unconfirmed_lab(authoritative):
    profile = ComplianceService(authoritative).analyse(ProductAnalyseRequest(description="5 litre domestic pressure cooker", as_of_date=date(2026, 9, 4)))
    assert profile.applicable_standards[0].version == "2023"
    assert not profile.laboratories
    assert any("laboratory recognition validity" in item for item in profile.coverage.known_limitations)


def test_hallmarking_temporal_resolution_and_huid_boundary(authoritative):
    service = ComplianceService(authoritative)
    old = service.analyse(ProductAnalyseRequest(description="22K916 gold jewellery with HUID", as_of_date=date(2022, 1, 1)))
    current = service.analyse(ProductAnalyseRequest(description="22K916 gold jewellery with HUID", as_of_date=date(2026, 9, 4)))
    assert old.qco.notification_number == "S.O. 2102(E)"
    assert old.qco.status.value == "ACTIVE"
    assert current.qco.notification_number == "S.O. 4345(E)"
    assert any("BIS Care" in action for action in current.consumer_actions)
    assert current.hallmarking_centres == []


def test_coverage_registry_and_120_case_benchmark(authoritative):
    records = CoverageRepository(authoritative).list()
    assert {item.product_category.slug for item in records} == {
        "appliances-for-heating-liquids", "motorcycle-helmet", "ordinary-portland-cement", "domestic-pressure-cooker", "gold-jewellery",
    }
    assert len(CASES) >= 120
    links = list(authoritative.scalars(select(TestStandardRelationshipRecord)))
    assert {item.referenced_standard_id for item in links} == {"is-4031-part-6-1988-auth", "is-4032-1985-auth"}


def test_product_attribute_extraction_and_no_material_inference():
    assert classify_authoritative("OPC 43S cement")["structured"]["grade"] == "43S"
    assert classify_authoritative("7.5 litre pressure cooker")["structured"]["capacity_l"] == 7.5
    assert classify_authoritative("22K916 gold jewellery")["structured"]["declared_fineness"] == "22K916"
    assert "material and construction type" in classify_authoritative("7.5 litre pressure cooker")["missing"]


def test_phase_2e_api_surfaces(client, authoritative):
    coverage = client.get("/api/v1/coverage")
    stats = client.get("/api/v1/coverage/stats")
    guidance = client.get("/api/v1/hallmarking/guidance")
    assert coverage.status_code == stats.status_code == guidance.status_code == 200
    assert len(coverage.json()) == 5
    assert stats.json()["verified"] == 3
    assert {item["topic"] for item in guidance.json()} == {"verify-huid", "identify-hallmark", "consumer-testing"}
