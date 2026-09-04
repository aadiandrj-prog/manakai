from __future__ import annotations

import re


def classify_authoritative(description: str) -> dict:
    text = description.casefold()
    voltage = re.search(r"(?<!\d)(\d{2,4})\s*(?:v|volt|volts|वोल्ट)\b", text)
    power = re.search(r"(?<!\d)(\d{2,5})\s*(?:w(?:att)?s?|वाट)\b", text)
    power_kw = re.search(r"(?<![\d.])(\d+(?:\.\d+)?)\s*k(?:ilo)?w\b", text)
    common = {"country": "India" if any(term in text for term in ("india", "indian", "भारत", "bis")) else None}

    if any(term in text for term in ("electric kettle", "kettle", "electric jug", "water boiler", "केतली")):
        household = any(term in text for term in ("household", "domestic", "home", "ghar", "घरेलू", "घर"))
        commercial = any(term in text for term in ("commercial", "hotel", "restaurant", "व्यावसायिक"))
        watts = int(power.group(1)) if power else int(float(power_kw.group(1)) * 1000) if power_kw else None
        structured = {**common, "product_type": "electric_kettle", "category": "appliances_for_heating_liquids", "intended_use": "household" if household else "commercial" if commercial else None, "rated_power_w": watts}
        if voltage: structured["rated_voltage_v"] = int(voltage.group(1))
        attributes = ["Electric kettle", "Appliance for heating liquids"] + ([f"{watts} W rated power"] if watts else []) + (["Household use"] if household else [])
        return {"category_slug": "appliances-for-heating-liquids", "category": "Appliances for Heating Liquids", "attributes": attributes, "structured": structured, "missing": ["rated voltage"] if not voltage else [], "confidence": .98}

    helmet = any(term in text for term in ("helmet", "हेलमेट"))
    motorcycle = any(term in text for term in ("motorcycle", "motorbike", "bike rider", "two wheeler", "two-wheeler", "rider", "मोटरसाइकिल", "दोपहिया"))
    if helmet and not motorcycle:
        return {"category_slug": None, "category": "Ambiguous helmet", "attributes": ["Helmet"], "structured": {**common, "product_type": "helmet", "candidate_categories": ["motorcycle-helmet", "industrial-safety-helmet", "sports-helmet"]}, "missing": ["helmet intended use"], "confidence": .35, "ambiguous": True}
    if helmet and motorcycle:
        attributes = ["Protective helmet", "Motorcycle rider use"]
        return {"category_slug": "motorcycle-helmet", "category": "Protective helmets for motorcycle riders", "attributes": attributes, "structured": {**common, "product_type": "motorcycle_helmet", "category": "motorcycle_helmet"}, "missing": [], "confidence": .97}

    if any(term in text for term in ("ordinary portland cement", "portland cement", "opc", "ओपीसी", "सीमेंट")):
        grade = re.search(r"\b(?:opc\s*)?(33|43s?|53s?)\s*(?:grade)?\b", text)
        attributes = ["Ordinary Portland Cement"] + ([f"Grade {grade.group(1).upper()}"] if grade else [])
        return {"category_slug": "ordinary-portland-cement", "category": "Ordinary Portland Cement", "attributes": attributes, "structured": {**common, "product_type": "ordinary_portland_cement", "category": "ordinary_portland_cement", "grade": grade.group(1).upper() if grade else None}, "missing": [] if grade else ["OPC grade"], "confidence": .96 if grade else .9}

    if any(term in text for term in ("pressure cooker", "प्रेशर कुकर", "कुकर")):
        capacity = re.search(r"(\d+(?:\.\d+)?)\s*(?:l|litre|liter|लीटर)\b", text)
        attributes = ["Domestic pressure cooker"] + ([f"{capacity.group(1)} litre capacity"] if capacity else [])
        return {"category_slug": "domestic-pressure-cooker", "category": "Domestic Pressure Cooker", "attributes": attributes, "structured": {**common, "product_type": "domestic_pressure_cooker", "category": "domestic_pressure_cooker", "capacity_l": float(capacity.group(1)) if capacity else None}, "missing": ["material and construction type"], "confidence": .96}

    if any(term in text for term in ("gold jewellery", "gold jewelry", "gold ornament", "सोने के आभूषण", "सोने का गहना", "hallmark", "huid")):
        combined = re.search(r"\b(14|18|20|22|23|24)\s*k\s*(585|750|833|916|958|995)\b", text)
        carat = re.search(r"\b(14|18|20|22|23|24)\s*(?:k|karat|carat)\b", text)
        fineness = re.search(r"\b(585|750|833|916|958|995)\b", text)
        declared = f"{combined.group(1)}K{combined.group(2)}" if combined else f"{carat.group(1)}K" if carat else fineness.group(1) if fineness else None
        attributes = ["Gold jewellery or artefact"] + ([f"Declared fineness: {declared}"] if declared else [])
        return {"category_slug": "gold-jewellery", "category": "Gold Jewellery and Gold Artefacts", "attributes": attributes, "structured": {**common, "product_type": "gold_jewellery", "category": "gold_jewellery", "declared_fineness": declared}, "missing": [] if declared else ["declared carat/fineness"], "confidence": .96}

    return {"category_slug": None, "category": "Unsupported product", "attributes": [], "structured": {**common, "product_type": None, "candidate_categories": []}, "missing": [], "confidence": .1, "unsupported": True}
