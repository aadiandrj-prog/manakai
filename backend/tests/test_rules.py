from datetime import date

from app.services.rules import QCORecord, evaluate_certification, prefer_current_version


def test_unverified_qco_never_creates_mandatory_claim():
    qco = QCORecord("IS DEMO", date(2024, 1, 1), "ACTIVE", source_verified=False)
    assert evaluate_certification(qco, date(2026, 1, 1)) == "UNVERIFIED"


def test_active_verified_effective_qco_is_mandatory():
    qco = QCORecord("IS DEMO", date(2024, 1, 1), "ACTIVE", source_verified=True)
    assert evaluate_certification(qco, date(2026, 1, 1)) == "MANDATORY"


def test_future_qco_is_upcoming():
    qco = QCORecord("IS DEMO", date(2027, 1, 1), "ACTIVE", source_verified=True)
    assert evaluate_certification(qco, date(2026, 1, 1)) == "UPCOMING"


def test_active_version_beats_superseded_newer_label():
    records = [
        {"version": "2025", "status": "SUPERSEDED", "effective_date": "2025-01-01"},
        {"version": "2024+A1", "status": "ACTIVE", "effective_date": "2026-02-01"},
    ]
    assert prefer_current_version(records)["status"] == "ACTIVE"
