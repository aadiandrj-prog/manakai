from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path


REGISTRY_PATH = Path(__file__).resolve().parent / "data" / "product_families.json"


def _normalise(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(re.sub(r"[^\w\u0900-\u097f.]+", " ", value).split())


@lru_cache(maxsize=1)
def load_family_registry() -> tuple[dict, ...]:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("Unsupported product-family registry schema")
    families = payload.get("families", [])
    slugs = [item["slug"] for item in families]
    if len(slugs) != len(set(slugs)):
        raise ValueError("Product-family slugs must be unique")
    return tuple(families)


def public_family_suggestions(query: str = "", *, limit: int = 12) -> list[dict]:
    needle = _normalise(query)
    matches = []
    for family in load_family_registry():
        haystack = _normalise(" ".join([family["name"], family["slug"], *family.get("aliases", [])]))
        if needle and needle not in haystack:
            continue
        matches.append({"slug": family["slug"], "name": family["name"], "product_group": family["group"], "aliases": family.get("aliases", [])[:5], "coverage_status": family["coverage_status"]})
    return matches[: max(1, min(limit, 50))]


def _extract_attributes(text: str, product_type: str) -> dict:
    attrs: dict[str, str | int | float | None] = {}
    patterns = {
        "rated_voltage_v": r"(?<!\d)(\d{2,4})\s*(?:v|volt|volts|वोल्ट)\b",
        "rated_power_w": r"(?<!\d)(\d{2,5})\s*(?:w(?:att)?s?|वाट)\b",
        "capacity_l": r"(\d+(?:\.\d+)?)\s*(?:l|litre|liter|लीटर)\b",
        "rated_current_a": r"(\d+(?:\.\d+)?)\s*(?:a|amp|amps|ampere)\b",
        "thickness_mm": r"(\d+(?:\.\d+)?)\s*mm\b",
    }
    for field, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            attrs[field] = int(match.group(1)) if field in {"rated_voltage_v", "rated_power_w"} else float(match.group(1))
    power_kw = re.search(r"(?<![\d.])(\d+(?:\.\d+)?)\s*k(?:ilo)?w\b", text)
    if power_kw and "rated_power_w" not in attrs:
        attrs["rated_power_w"] = int(float(power_kw.group(1)) * 1000)
    household = any(term in text for term in ("household", "domestic", "home", "घर", "घरेलू"))
    commercial = any(term in text for term in ("commercial", "hotel", "restaurant", "व्यावसायिक"))
    if product_type == "motorcycle_helmet":
        attrs["intended_use"] = "motorcycle rider"
    elif household or product_type in {"domestic_pressure_cooker", "domestic_lpg_stove"}:
        attrs["intended_use"] = "household"
    elif commercial:
        attrs["intended_use"] = "commercial"
    if any(term in text for term in ("india", "indian", "भारत", "bis")):
        attrs["country"] = "India"
    if product_type == "ordinary_portland_cement":
        grade = re.search(r"\b(?:opc\s*)?(33|43s?|53s?)\s*(?:grade)?\b", text)
        if grade:
            attrs["grade"] = grade.group(1).upper()
    if product_type == "gold_jewellery":
        combined = re.search(r"\b(14|18|20|22|23|24)\s*k\s*(585|750|833|916|958|995)\b", text)
        carat = re.search(r"\b(14|18|20|22|23|24)\s*(?:k|karat|carat)\b", text)
        fineness = re.search(r"\b(585|750|833|916|958|995)\b", text)
        if combined: attrs["declared_fineness"] = f"{combined.group(1)}K{combined.group(2)}"
        elif carat: attrs["declared_fineness"] = f"{carat.group(1)}K"
        elif fineness: attrs["declared_fineness"] = fineness.group(1)
    if product_type == "domestic_lpg_stove" and any(term in text for term in ("lpg", "liquefied petroleum", "एलपीजी")):
        attrs["fuel_type"] = "LPG"
    if product_type == "skin_hair_care_appliance":
        for term, value in (("dryer", "hair_dryer"), ("straightener", "hair_straightener"), ("curler", "hair_curler"), ("ड्रायर", "hair_dryer")):
            if term in text: attrs["appliance_type"] = value; break
    if product_type == "electrical_appliance_fan":
        for term in ("table", "pedestal", "wall", "exhaust"):
            if term in text: attrs["fan_type"] = term; break
    if product_type == "safety_glass":
        if "automotive" in text or "vehicle" in text: attrs.update(intended_use="automotive", glass_part="Part 2 candidate")
        elif any(term in text for term in ("architectural", "building", "general purpose")): attrs.update(intended_use="general purpose", glass_part="Part 1 candidate")
    return attrs


def classify_from_registry(description: str) -> dict:
    text = _normalise(description)
    matches: list[tuple[int, dict]] = []
    for family in load_family_registry():
        for alias in family.get("aliases", []):
            alias = _normalise(alias)
            if alias and re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", text):
                matches.append((len(alias), family))
    if matches:
        matches.sort(key=lambda item: (-item[0], item[1]["slug"]))
        top_length = matches[0][0]
        top = {item[1]["slug"]: item[1] for item in matches if item[0] == top_length}
        if len(top) > 1:
            return _ambiguous(sorted(top), text)
        family = matches[0][1]
        structured = {"product_type": family["product_type"], "category": family.get("structured_category", family["product_type"]), **_extract_attributes(text, family["product_type"])}
        missing = [field for field in family.get("required_attributes", []) if structured.get(field) in (None, "")]
        attributes = [family["name"]] + [f"{key.replace('_', ' ')}: {value}" for key, value in structured.items() if key not in {"product_type", "category"} and value is not None]
        return {"category_slug": family["slug"], "category": family["name"], "attributes": attributes, "structured": structured, "missing": missing, "confidence": .97 if not missing else .88}
    candidates: list[str] = []
    for family in load_family_registry():
        if any(re.search(rf"(?<!\w){re.escape(_normalise(term))}(?!\w)", text) for term in family.get("ambiguity_terms", [])):
            candidates.extend(family.get("ambiguity_candidates", [family["slug"]]))
    if candidates:
        return _ambiguous(sorted(set(candidates)), text)
    return {"category_slug": None, "category": "Unsupported product", "attributes": [], "structured": {"product_type": None, "country": "India" if any(term in text for term in ("india", "भारत", "bis")) else None, "candidate_categories": []}, "missing": [], "confidence": .1, "unsupported": True}


def _ambiguous(candidates: list[str], text: str) -> dict:
    return {"category_slug": None, "category": "Ambiguous product family", "attributes": [], "structured": {"product_type": None, "country": "India" if any(term in text for term in ("india", "भारत", "bis")) else None, "candidate_categories": candidates}, "missing": ["product subtype or intended use"], "confidence": .35, "ambiguous": True}
