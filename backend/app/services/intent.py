import re

from ..schemas import Intent


def classify_intent(query: str) -> Intent:
    text = query.casefold()
    if any(term in text for term in ("huid", "hallmark", "jewellery", "jewelry")):
        return Intent.HALLMARKING_QUERY
    if any(term in text for term in ("lab", "laboratory", "testing near", "test near")):
        return Intent.LAB_SEARCH
    if re.search(r"\bIS\s*\d{3,}", query) or any(term in text for term in ("clause", "what does is ", "standard say", "amendment", "bis guide")):
        return Intent.STANDARD_QA
    if any(term in text for term in ("mandatory", "certification", "qco", "licence", "license", "requirement", "required", "bis ka kya", "बीआईएस")):
        return Intent.CERTIFICATION_QUERY
    if any(term in text for term in ("manufacture", "import", "product", "kettle", "केतली", "बनाता", "बनाती", "lamp", "helmet", "cement", "opc", "pressure cooker", "कुकर", "सीमेंट", "मोटरसाइकिल")):
        return Intent.PRODUCT_COMPLIANCE
    if any(term in text for term in ("consumer", "complaint", "mark")):
        return Intent.CONSUMER_QUERY
    if any(term in text for term in ("bis", "bureau of indian standards", "भारतीय मानक")):
        return Intent.GENERAL_BIS_QUERY
    return Intent.UNKNOWN
