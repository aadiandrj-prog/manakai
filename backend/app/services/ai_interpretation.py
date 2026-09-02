from __future__ import annotations

import re
from datetime import date

from ..schemas import (
    ClarificationDecision, ConversationInterpretation, Intent, IntentClassification, ProductExtraction, SupportedLanguage,
)
from .intent import classify_intent

MONTHS = {name.lower(): index for index, name in enumerate(("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), 1)}


def detect_language(text: str, preference: str = "auto") -> SupportedLanguage:
    if preference in {"en", "hi", "hinglish"}:
        return SupportedLanguage(preference)
    if re.search(r"[\u0900-\u097f]", text):
        return SupportedLanguage.HINDI
    lower = text.casefold()
    if any(token in lower.split() for token in ("ka", "ke", "ki", "ghar", "wala", "liye", "kya", "hai", "hum", "kar", "raha", "hu")):
        return SupportedLanguage.HINGLISH
    return SupportedLanguage.ENGLISH


def _number(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text, re.I)
    return int(float(match.group(1)) * (1000 if match.lastgroup == "kw" else 1)) if match else None


def extract_product(text: str, previous: dict | None = None) -> ProductExtraction | None:
    lower = text.casefold()
    normalized = re.sub(r"(?<=\d),(?=\d)", "", lower)
    previous = previous or {}
    kettle = any(term in lower for term in ("kettle", "electric jug", "water boiler", "केतली")) or previous.get("product_type") == "electric_kettle"
    if not kettle:
        return ProductExtraction.model_validate(previous) if previous.get("product_type") else None
    power_kw = re.search(r"(?P<kw>\d+(?:\.\d+)?)\s*k(?:ilo)?w\b", normalized)
    power_w = re.search(r"(?<![\d.])(\d{2,5})\s*(?:w(?:att)?s?|वाट)\b", normalized)
    voltage_range = re.search(r"(?<!\d)(\d{2,4})\s*[-–]\s*(\d{2,4})\s*(?:v|volt|volts)\b", normalized)
    voltage = re.search(r"(?<!\d)(\d{2,4})\s*(?:v|volt|volts|वोल्ट)\b", normalized)
    household = any(term in lower for term in ("household", "house use", "domestic", "home", "homes", "ghar", "घरेलू", "घर"))
    commercial = any(term in lower for term in ("commercial", "hotel", "restaurant", "व्यावसायिक", "होटल", "रेस्तरां"))
    enterprise = None
    if re.search(r"\bmicro\s+(?:enterprise|business|startup)|सूक्ष्म\s+(?:उद्यम|व्यवसाय)", lower): enterprise = "MICRO"
    elif re.search(r"\bsmall\s+(?:enterprise|business|startup)|लघु\s+(?:उद्यम|व्यवसाय)", lower): enterprise = "SMALL"
    actor = "manufacturer" if any(term in lower for term in ("manufactur", "make ", "planning to make", "बनाता", "बनाती", "बनाते", "निर्माण")) else previous.get("actor")
    values = {
        **previous,
        "product_type": "electric_kettle",
        "category": "appliances_for_heating_liquids",
        "actor": actor,
        "intended_use": "household" if household else "commercial" if commercial else previous.get("intended_use"),
        "rated_power_w": int(float(power_kw.group("kw")) * 1000) if power_kw else int(power_w.group(1)) if power_w else previous.get("rated_power_w"),
        "rated_voltage_v": int(voltage_range.group(2)) if voltage_range else int(voltage.group(1)) if voltage else previous.get("rated_voltage_v"),
        "country": "India" if any(term in lower for term in ("india", "indian", "bis", "भारत")) else previous.get("country"),
        "enterprise_category": enterprise or previous.get("enterprise_category"),
        "additional_attributes": {
            **previous.get("additional_attributes", {}),
            **({"cordless": True} if "cordless" in lower else {}),
            **({"rated_voltage_range_v": f"{voltage_range.group(1)}-{voltage_range.group(2)}"} if voltage_range else {}),
        },
        "confidence": 0.97 if voltage and (household or previous.get("intended_use")) else 0.88,
    }
    values["missing_required_fields"] = [field for field in ("rated_voltage_v",) if values.get(field) is None]
    return ProductExtraction.model_validate(values)


def extract_date(text: str) -> date | None:
    iso = re.search(r"\b(20\d{2})-(\d{2})-(\d{2})\b", text)
    if iso:
        return date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
    named = re.search(r"\b(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})\b", text)
    if named and named.group(2).casefold() in MONTHS:
        return date(int(named.group(3)), MONTHS[named.group(2).casefold()], int(named.group(1)))
    return None


def interpret(text: str, *, preference: str = "auto", previous: dict | None = None) -> ConversationInterpretation:
    language = detect_language(text, preference)
    routed_intent = classify_intent(text)
    product = extract_product(text, previous)
    if product and routed_intent in {Intent.UNKNOWN, Intent.CERTIFICATION_QUERY, Intent.GENERAL_BIS_QUERY}:
        routed_intent = Intent.PRODUCT_COMPLIANCE
    confidence = 0.94 if routed_intent.value != "UNKNOWN" else 0.2
    missing = product.missing_required_fields if product else []
    return ConversationInterpretation(
        language=language,
        intent=IntentClassification(intent=routed_intent, confidence=confidence, route_reason="deterministic pattern route"),
        product=product,
        as_of_date=extract_date(text),
        clarification=ClarificationDecision(required=bool(missing), fields=missing),
    )
