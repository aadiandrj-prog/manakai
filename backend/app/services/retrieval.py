from ..fixtures import CITATIONS, STANDARDS


def search_standards(query: str):
    terms = {term for term in query.casefold().split() if len(term) > 2}
    scored = []
    for standard in STANDARDS:
        haystack = f"{standard.number} {standard.title} {standard.category} {standard.scope}".casefold()
        score = sum(term in haystack for term in terms)
        if score:
            scored.append((score, standard))
    return [item for _, item in sorted(scored, key=lambda pair: pair[0], reverse=True)]


def retrieve_citations(query: str):
    text = query.casefold()
    if any(term in text for term in ("huid", "hallmark", "jewellery")):
        return [citation for citation in CITATIONS if citation.id == "cite-huid-guide"]
    if any(term in text for term in ("emergency", "luminaire", "10322")):
        return [citation for citation in CITATIONS if "emergency" in citation.id]
    return []
