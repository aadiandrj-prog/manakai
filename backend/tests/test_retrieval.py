from app.services.retrieval import retrieve_citations, search_standards


def test_hybrid_fixture_search_matches_number_and_title_terms():
    results = search_standards("emergency lighting 10322")
    assert results[0].id == "is-10322-5-8"


def test_hallmarking_retrieval_uses_consumer_fixture():
    citations = retrieve_citations("How do I verify a HUID?")
    assert citations[0].id == "cite-huid-guide"
