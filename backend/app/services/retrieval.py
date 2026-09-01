from sqlalchemy.orm import Session

from ..config import settings
from ..repositories import DocumentRepository, StandardRepository
from ..schemas import Citation, QueryResponse
from ..serializers import citation_to_schema, standard_to_schema
from .intent import classify_intent
from .embeddings import provider_from_settings
from .hybrid import HybridRetrievalService


class RetrievalService:
    def __init__(self, session: Session):
        self.session = session
        self.standards = StandardRepository(session)
        self.documents = DocumentRepository(session)

    def search_standards(self, query: str):
        expected = "DEMO" if settings.demo_mode else "AUTHORITATIVE"
        return [standard_to_schema(item) for item in self.standards.search(query) if item.source_kind == expected or (not settings.demo_mode and item.source_kind == "VERIFIED_DERIVED")]

    def answer(self, query: str) -> QueryResponse:
        intent = classify_intent(query)
        if not settings.demo_mode:
            ranked = HybridRetrievalService(self.session, provider_from_settings(settings.embedding_provider)).search(query)
            citations = []
            for result in ranked:
                document = result.chunk.document
                if document.verification_status not in {"AUTHORITATIVE", "VERIFIED_DERIVED"} or document.status in {"SUPERSEDED", "WITHDRAWN"}:
                    continue
                citations.append(Citation(
                    id=f"retrieval-{result.chunk.id}", document_title=document.title, document_type=document.document_type,
                    standard_number=document.standard.number if document.standard else None, version=document.version,
                    page=result.chunk.page, clause=result.chunk.clause, source_url=document.source_url,
                    publication_date=document.publication_date, effective_date=document.effective_date, retrieved_at=document.retrieved_at,
                    source_kind=document.source_kind, source_authority=document.source_authority,
                    document_identifier=document.document_identifier, status=document.status,
                    verification_status=document.verification_status, claim="Retrieved evidence candidate", validation_status="VALID",
                ))
            if citations:
                return QueryResponse(intent=intent, answer="Authoritative evidence candidates were retrieved using exact metadata, PostgreSQL lexical search and configured vector ranking. Review the cited clauses/pages; no generative model made a regulatory decision.", citations=citations, confidence=min(0.95, 0.65 + 0.05 * len(citations)), warnings=[])
            return QueryResponse(intent=intent, answer="I could not verify this requirement from the ingested authoritative BIS sources.", citations=[], confidence=0.0, warnings=["The authoritative corpus currently covers only the electric-kettle vertical."])
        citations = [citation_to_schema(item) for item in self.documents.search_citations(query)]
        if citations:
            answer = "The demo database contains relevant structured evidence, but no authoritative clause text is connected. I can explain the workflow while keeping the legal claim unverified."
        else:
            answer = "I could not verify this requirement from the available authorised BIS sources."
        return QueryResponse(
            intent=intent,
            answer=answer,
            citations=citations,
            confidence=0.62 if citations else 0.0,
            warnings=["DEMO_MODE is active", "Verify against current official sources"],
        )
