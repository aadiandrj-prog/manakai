from app.services.retrieval import RetrievalService


def test_database_search_matches_number_and_title_terms(db_session):
    results = RetrievalService(db_session).search_standards("emergency lighting 10322")
    assert results[0].id == "is-10322-5-8"


def test_hallmarking_retrieval_uses_database_evidence(db_session):
    citations = RetrievalService(db_session).answer("How do I verify a HUID?").citations
    assert citations[0].id == "cite-huid-guide"
