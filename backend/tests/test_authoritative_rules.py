from datetime import date

from app.services.rules import QCORecord, evaluate_certification, temporal_status


def qco(effective=date(2026, 10, 1), **changes):
    values = dict(standard_number="IS 302 (Part 1)", effective_date=effective, status="NOTIFIED", source_verified=True, notification_date=date(2026, 4, 6))
    values.update(changes)
    return QCORecord(**values)


def test_qco_date_resolution_before_notification_upcoming_effective_and_after():
    assert temporal_status(qco(), date(2026, 4, 5)) == "UNKNOWN"
    assert temporal_status(qco(), date(2026, 9, 2)) == "UPCOMING"
    assert temporal_status(qco(), date(2026, 10, 1)) == "ACTIVE"
    assert temporal_status(qco(), date(2027, 1, 1)) == "ACTIVE"
    assert evaluate_certification(qco(), date(2026, 9, 2)) == "UPCOMING"
    assert evaluate_certification(qco(), date(2026, 10, 1)) == "MANDATORY"


def test_enterprise_dates_are_not_collapsed():
    assert temporal_status(qco(date(2026, 10, 1)), date(2026, 12, 1)) == "ACTIVE"
    assert temporal_status(qco(date(2027, 1, 1)), date(2026, 12, 1)) == "UPCOMING"
    assert temporal_status(qco(date(2027, 4, 1)), date(2026, 12, 1)) == "UPCOMING"


def test_superseded_qco_never_becomes_active():
    assert temporal_status(qco(status="SUPERSEDED", superseded=True), date(2027, 1, 1)) == "SUPERSEDED"
    assert evaluate_certification(qco(status="SUPERSEDED", superseded=True), date(2027, 1, 1)) == "NOT_MANDATORY_FROM_THIS_QCO"
