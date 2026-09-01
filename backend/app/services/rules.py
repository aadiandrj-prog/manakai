from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class QCORecord:
    standard_number: str
    effective_date: date | None
    status: str
    source_verified: bool
    notification_date: date | None = None
    effective_until: date | None = None
    superseded: bool = False


def temporal_status(qco: QCORecord, on_date: date) -> str:
    if qco.superseded or qco.status in {"SUPERSEDED", "WITHDRAWN"}:
        return qco.status if qco.status in {"SUPERSEDED", "WITHDRAWN"} else "SUPERSEDED"
    if not qco.source_verified:
        return "UNKNOWN"
    if qco.notification_date and on_date < qco.notification_date:
        return "UNKNOWN"
    if qco.effective_date and on_date < qco.effective_date:
        return "UPCOMING"
    if qco.effective_until and on_date > qco.effective_until:
        return "SUPERSEDED"
    if qco.effective_date and on_date >= qco.effective_date:
        return "ACTIVE"
    return "NOTIFIED"


def evaluate_certification(qco: QCORecord | None, on_date: date | None = None) -> str:
    """Only a current, verified, active QCO can produce a mandatory decision."""
    if qco is None or not qco.source_verified or qco.effective_date is None:
        return "UNVERIFIED"
    status = temporal_status(qco, on_date or date.today())
    if status == "ACTIVE":
        return "MANDATORY"
    if status == "UPCOMING":
        return "UPCOMING"
    return "NOT_MANDATORY_FROM_THIS_QCO"


def prefer_current_version(records: list[dict], on_date: date | None = None) -> dict | None:
    """Prefer active records, then effective date, preventing an older fixture from winning silently."""
    if not records:
        return None
    decision_date = on_date or date.today()
    eligible = [record for record in records if not record.get("notification_date") or record["notification_date"] <= decision_date]
    if not eligible:
        return None
    current = [record for record in eligible if record.get("status") not in {"SUPERSEDED", "WITHDRAWN"}]
    candidates = current or eligible
    status_priority = {"ACTIVE": 4, "AMENDED": 3, "NOTIFIED": 2, "UPCOMING": 1, "SUPERSEDED": 0, "WITHDRAWN": -1}
    return max(candidates, key=lambda item: (item.get("notification_date") or date.min, status_priority.get(item.get("status"), -2), item.get("effective_date") or "0000-00-00", item.get("version") or ""))
