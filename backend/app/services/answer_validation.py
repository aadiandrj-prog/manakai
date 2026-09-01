from __future__ import annotations

import re

from pydantic import BaseModel

from ..schemas import RegulatoryAnswerPackage


class GeneratedAnswer(BaseModel):
    answer: str
    evidence_ids: list[str] = []


class GeneratedAnswerValidator:
    def validate(self, generated: GeneratedAnswer, package: RegulatoryAnswerPackage) -> tuple[bool, str | None]:
        allowed_ids = {item.evidence_id for item in package.evidence}
        textual_ids = set(re.findall(r"\bE\d+\b", generated.answer))
        if any(item not in allowed_ids for item in {*generated.evidence_ids, *textual_ids}):
            return False, "Generated answer referenced an unknown evidence ID"
        profile = package.compliance_result
        if not profile:
            return True, None
        critical = [item.number for item in profile.applicable_standards]
        if profile.qco:
            critical += [profile.qco.notification_number or "", profile.qco.status.value, profile.qco.effective_from.isoformat() if profile.qco.effective_from else ""]
        if profile.certification_scheme:
            critical.append(profile.certification_scheme)
        found_standards = set(re.findall(r"IS\s+\d+(?:\s*\([^)]*\))?(?::\d{4})?", generated.answer, re.I))
        if found_standards and not all(any(found.casefold() in allowed.casefold() or allowed.casefold() in found.casefold() for allowed in critical) for found in found_standards):
            return False, "Generated answer introduced an unsupported standard identifier"
        qco_ids = set(re.findall(r"S\.O\.\s*\d+\([A-Z]\)", generated.answer, re.I))
        if qco_ids and (not profile.qco or any(item.casefold() != (profile.qco.notification_number or "").casefold() for item in qco_ids)):
            return False, "Generated answer introduced an unsupported QCO identifier"
        for status in ("ACTIVE", "UPCOMING", "SUPERSEDED", "WITHDRAWN"):
            if status in generated.answer.upper() and (not profile.qco or status != profile.qco.status.value):
                return False, "Generated answer contradicted QCO status"
        dates = set(re.findall(r"\b20\d{2}-\d{2}-\d{2}\b", generated.answer))
        allowed_dates = {profile.as_of_date.isoformat()}
        if profile.qco and profile.qco.effective_from:
            allowed_dates.add(profile.qco.effective_from.isoformat())
        if dates - allowed_dates:
            return False, "Generated answer introduced an unsupported regulatory date"
        named_dates = set(re.findall(r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d{2}\b", generated.answer, re.I))
        allowed_named_dates = {f"{value.day} {value.strftime('%B %Y')}".casefold() for value in [profile.as_of_date, *([profile.qco.effective_from] if profile.qco and profile.qco.effective_from else [])]}
        if any(item.casefold() not in allowed_named_dates for item in named_dates):
            return False, "Generated answer introduced an unsupported regulatory date"
        schemes = set(re.findall(r"Scheme\s+[IVX]+(?:\s*\([^)]*\))?", generated.answer, re.I))
        if schemes and (not profile.certification_scheme or any(item.casefold() not in profile.certification_scheme.casefold() for item in schemes)):
            return False, "Generated answer introduced an unsupported certification scheme"
        lab_names = set(re.findall(r"[A-Z][A-Za-z&,. -]{2,80}(?:Laboratory|Test House|Testing Centre)", generated.answer))
        allowed_labs = {item.name.casefold() for item in profile.laboratories}
        if any(not any(item.strip().casefold() in allowed or allowed in item.strip().casefold() for allowed in allowed_labs) for item in lab_names):
            return False, "Generated answer introduced an unsupported laboratory recognition"
        return True, None
