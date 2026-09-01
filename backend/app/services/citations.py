from dataclasses import dataclass

from sqlalchemy.orm import Session

from ..db_models import Citation, Document, DocumentChunk


@dataclass(frozen=True)
class CitationValidation:
    valid: bool
    error: str | None = None


class CitationValidationService:
    def __init__(self, session: Session):
        self.session = session

    def validate(self, citation: Citation, *, require_current: bool = True) -> CitationValidation:
        document = self.session.get(Document, citation.document_id)
        if document is None:
            return CitationValidation(False, "referenced document does not exist")
        if document.verification_status not in {"AUTHORITATIVE", "VERIFIED_DERIVED"}:
            return CitationValidation(False, "document is not verified")
        if require_current and document.status in {"SUPERSEDED", "WITHDRAWN"}:
            return CitationValidation(False, "document is not current")
        if citation.chunk_id:
            chunk = self.session.get(DocumentChunk, citation.chunk_id)
            if chunk is None or chunk.document_id != document.id:
                return CitationValidation(False, "clause/page chunk does not belong to the document")
            claim_terms = {term.casefold() for term in citation.claim.split() if len(term) > 4}
            evidence = chunk.text.casefold()
            if claim_terms and not any(term in evidence for term in claim_terms):
                return CitationValidation(False, "claim is not supported by stored evidence text")
        return CitationValidation(True)

    def mark(self, citation: Citation, *, require_current: bool = True) -> CitationValidation:
        result = self.validate(citation, require_current=require_current)
        citation.validation_status = "VALID" if result.valid else "INVALID"
        citation.validation_error = result.error
        return result
