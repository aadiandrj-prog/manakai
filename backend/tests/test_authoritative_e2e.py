from dataclasses import replace
from datetime import date

from sqlalchemy import select

from app.db_models import IngestionRun, LaboratoryRecognition, ProvenanceLink, SourceRecord
from app.ingestion.pipeline import ingest_electric_kettle
from app.schemas import ProductAnalyseRequest
import app.services.compliance as compliance_module
from app.services.compliance import ComplianceService


def test_authoritative_electric_kettle_end_to_end(db_session, monkeypatch):
    result = ingest_electric_kettle(db_session)
    monkeypatch.setattr(compliance_module, "settings", replace(compliance_module.settings, demo_mode=False))
    profile = ComplianceService(db_session).analyse(ProductAnalyseRequest(
        description="I manufacture a 1500 W electric kettle for household use in India.",
        as_of_date=date(2026, 9, 2), enterprise_category="GENERAL",
    ))
    assert result["status"] == "SUCCESS"
    assert profile.product.structured_attributes == {
        "product_type": "electric_kettle", "category": "appliances_for_heating_liquids", "intended_use": "household", "rated_power_w": 1500, "country": "India"
    }
    assert [item.number for item in profile.applicable_standards] == ["IS 302 (Part 2/Sec 15)", "IS 302 (Part 1)"]
    assert profile.mandatory_status == "UPCOMING"
    assert profile.qco.notification_number == "S.O. 1739(E)"
    assert profile.qco.effective_from == date(2026, 10, 1)
    assert profile.certification_scheme == "Scheme I (ISI Mark Scheme)"
    assert len(profile.laboratories) == 2
    assert all(item.source_kind == "AUTHORITATIVE" for item in profile.evidence)
    assert all(item.validation_status == "VALID" for item in profile.evidence)
    assert any("Rated voltage was not supplied" in warning for warning in profile.warnings)
    assert profile.explanation[2].conclusion == "UPCOMING"


def test_expired_labs_are_filtered_by_query_date(db_session, monkeypatch):
    ingest_electric_kettle(db_session)
    monkeypatch.setattr(compliance_module, "settings", replace(compliance_module.settings, demo_mode=False))
    profile = ComplianceService(db_session).analyse(ProductAnalyseRequest(description="1500 W household electric kettle in India", as_of_date=date(2027, 2, 1)))
    assert [lab.name for lab in profile.laboratories] == ["Shri Krishna Test House"]


def test_ingestion_is_idempotent_and_provenance_is_authoritative(db_session):
    first = ingest_electric_kettle(db_session)
    second = ingest_electric_kettle(db_session)
    assert first["records_created"] > 0
    assert second["records_updated"] > 0
    assert len(db_session.scalars(select(SourceRecord)).all()) == 6
    assert all(item.verification_status == "AUTHORITATIVE" for item in db_session.scalars(select(SourceRecord)).all())
    assert len(db_session.scalars(select(ProvenanceLink)).all()) >= 5
    assert db_session.scalar(select(IngestionRun).order_by(IngestionRun.started_at.desc())).status == "SUCCESS"
