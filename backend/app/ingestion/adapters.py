from __future__ import annotations

from copy import deepcopy
from typing import Any

from .base import BISSourceAdapter, stable_hash


def _with_source(record: dict[str, Any], sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    result = deepcopy(record)
    source_key = result.pop("source")
    source = deepcopy(sources[source_key])
    source["content_hash"] = stable_hash(source)
    result["source_record"] = source
    return result


class BISStandardAdapter(BISSourceAdapter):
    name = "standards"

    def parse(self, raw: Any) -> Any:
        return raw

    def normalize(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return [_with_source(item, parsed["sources"]) for item in parsed.get("standards", [])]

    def validate(self, records: list[dict[str, Any]]) -> list[str]:
        errors = []
        for record in records:
            if not record.get("number") or not record.get("version"):
                errors.append("standard number and version are required")
            if record["source_record"].get("source_authority") not in {"Bureau of Indian Standards", "Department for Promotion of Industry and Internal Trade, Government of India"}:
                errors.append(f"{record.get('id')}: standard source is not BIS/government")
        return errors


class BISProductManualAdapter(BISSourceAdapter):
    name = "product-manuals"

    def parse(self, raw: Any) -> Any:
        return raw["sources"]["product_manual"]

    def normalize(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        source = deepcopy(parsed)
        source["content_hash"] = stable_hash(source)
        return [{
            "id": "manual-is-302-2-15-2024",
            "manual_identifier": parsed["document_identifier"],
            "standard_id": "is-302-2-15-auth",
            "status": "ACTIVE",
            "pages": parsed["pages"],
            "source_record": source,
        }]

    def validate(self, records: list[dict[str, Any]]) -> list[str]:
        return [] if records and records[0]["manual_identifier"] == "PM/IS 302-2-15/1/February 2024" else ["unexpected kettle product-manual identifier"]


class BISQCOAdapter(BISSourceAdapter):
    name = "qco"

    def parse(self, raw: Any) -> Any:
        return raw

    def normalize(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return [_with_source(item, parsed["sources"]) for item in parsed.get("qcos", [])]

    def validate(self, records: list[dict[str, Any]]) -> list[str]:
        errors = []
        categories = {"GENERAL", "SMALL", "MICRO"}
        for record in records:
            actual = {item["enterprise_category"] for item in record.get("applicability", [])}
            if actual != categories:
                errors.append(f"{record.get('id')}: incomplete enterprise implementation dates")
            if record.get("notification_number") != "S.O. 1739(E)":
                errors.append(f"{record.get('id')}: unexpected notification")
        return errors


class BISCompulsoryCertificationAdapter(BISSourceAdapter):
    name = "compulsory-certification"

    def parse(self, raw: Any) -> Any:
        return raw["sources"]["scheme_i"]

    def normalize(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        source = deepcopy(parsed)
        source["content_hash"] = stable_hash(source)
        return [{"id": "scheme-i-kettle-auth", "name": "Scheme I (ISI Mark Scheme)", "standard_id": "is-302-1-2024-auth", "qco_id": "qco-household-appliances-2026", "source_record": source}]

    def validate(self, records: list[dict[str, Any]]) -> list[str]:
        return [] if records and "Scheme I" in records[0]["name"] else ["Scheme I mapping not found"]


class BISLIMSAdapter(BISSourceAdapter):
    name = "labs"

    def parse(self, raw: Any) -> Any:
        return raw

    def normalize(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return [_with_source(item, parsed["sources"]) for item in parsed.get("laboratories", [])]

    def validate(self, records: list[dict[str, Any]]) -> list[str]:
        errors = []
        for record in records:
            if not record.get("valid_until"):
                errors.append(f"{record.get('id')}: validity date is required for authoritative recommendation")
            if record["source_record"].get("source_type") != "BIS_LIMS_SCOPE":
                errors.append(f"{record.get('id')}: source is not a LIMS scope")
        return errors
