from ..schemas import Intent


def classify_intent(query: str) -> Intent:
    text = query.casefold()
    if any(term in text for term in ("huid", "hallmark", "jewellery", "jewelry")):
        return Intent.HALLMARKING_QUERY
    if any(term in text for term in ("lab", "laboratory", "testing near", "test near")):
        return Intent.LAB_SEARCH
    if any(term in text for term in ("clause", "what does is ", "standard say", "amendment")):
        return Intent.STANDARD_QA
    if any(term in text for term in ("mandatory", "certification", "qco", "licence", "license")):
        return Intent.CERTIFICATION_QUERY
    if any(term in text for term in ("manufacture", "import", "product", "kettle", "lamp", "helmet")):
        return Intent.PRODUCT_COMPLIANCE
    if any(term in text for term in ("consumer", "complaint", "mark")):
        return Intent.CONSUMER_QUERY
    return Intent.GENERAL_BIS_QUERY
