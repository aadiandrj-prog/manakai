from app.db_models import Citation, DocumentChunk
from app.ingestion.pipeline import ingest_electric_kettle
from app.services.citations import CitationValidationService
from app.services.embeddings import EmbeddingProvider
from app.services.hybrid import HybridRetrievalService


class FakeEmbeddingProvider(EmbeddingProvider):
    def embed(self, texts):
        return [[1.0] + [0.0] * 383 for _ in texts]


def test_full_text_exact_clause_and_hybrid_ranking(db_session):
    ingest_electric_kettle(db_session)
    chunk = db_session.get(DocumentChunk, "chunk-kettle-manual-5")
    chunk.embedding = [1.0] + [0.0] * 383
    db_session.commit()
    results = HybridRetrievalService(db_session, FakeEmbeddingProvider()).search("IS 302-2-15 clause A.3(a) higher input rating")
    assert results
    assert results[0].chunk.id == "chunk-kettle-manual-5"
    assert "exact-clause" in results[0].reasons
    assert "vector" in results[0].reasons


def test_citation_validator_accepts_matching_chunk_and_rejects_wrong_document(db_session):
    ingest_electric_kettle(db_session)
    valid = Citation(id="valid-cite", document_id="doc-bis-kettle-guide", chunk_id="chunk-bis-kettle-guide", claim="electric kettles appliances heating liquids", source_kind="AUTHORITATIVE")
    db_session.add(valid)
    db_session.flush()
    service = CitationValidationService(db_session)
    assert service.validate(valid).valid is True
    valid.chunk_id = "chunk-qco-household-appliances-2026"
    assert service.validate(valid).valid is False
