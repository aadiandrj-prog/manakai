from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class QCORecord:
    standard_number: str
    effective_date: date
    status: str
    source_verified: bool


def evaluate_certification(qco: QCORecord | None, on_date: date | None = None) -> str:
    """Only a current, verified, active QCO can produce a mandatory decision."""
    if qco is None or not qco.source_verified:
        return "UNVERIFIED"
    decision_date = on_date or date.today()
    if qco.status == "ACTIVE" and decision_date >= qco.effective_date:
        return "MANDATORY"
    if decision_date < qco.effective_date:
        return "UPCOMING"
    return "NOT_MANDATORY_FROM_THIS_QCO"


def prefer_current_version(records: list[dict]) -> dict | None:
    """Prefer active records, then effective date, preventing an older fixture from winning silently."""
    if not records:
        return None
    status_priority = {"ACTIVE": 3, "AMENDED": 2, "UPCOMING": 1, "SUPERSEDED": 0, "WITHDRAWN": -1}
    return max(records, key=lambda item: (status_priority.get(item.get("status", ""), -2), item.get("effective_date") or "0000-00-00", item.get("version") or ""))
