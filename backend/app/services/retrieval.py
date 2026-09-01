from sqlalchemy.orm import Session

from ..repositories import DocumentRepository, StandardRepository
from ..schemas import QueryResponse
from ..serializers import citation_to_schema, standard_to_schema
from .intent import classify_intent


class RetrievalService:
    def __init__(self, session: Session):
        self.standards = StandardRepository(session)
        self.documents = DocumentRepository(session)

    def search_standards(self, query: str):
        return [standard_to_schema(item) for item in self.standards.search(query)]

    def answer(self, query: str) -> QueryResponse:
        intent = classify_intent(query)
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
