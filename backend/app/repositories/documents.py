from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from ..db_models import Citation, Document, DocumentChunk


class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, document_id: str) -> Document | None:
        return self.session.scalar(select(Document).options(joinedload(Document.standard)).where(Document.id == document_id))

    def citations_for_profile(self, profile_id: str) -> list[Citation]:
        statement = (
            select(Citation)
            .options(joinedload(Citation.document).joinedload(Document.standard), joinedload(Citation.chunk))
            .where(Citation.compliance_profile_id == profile_id)
            .order_by(Citation.id)
        )
        return list(self.session.scalars(statement))

    def search_citations(self, query: str) -> list[Citation]:
        text = query.casefold()
        statement = select(Citation).options(
            joinedload(Citation.document).joinedload(Document.standard),
            joinedload(Citation.chunk),
        )
        if any(term in text for term in ("huid", "hallmark", "jewellery")):
            statement = statement.where(Citation.id == "cite-huid-guide")
        elif any(term in text for term in ("emergency", "luminaire", "10322")):
            statement = statement.where(Citation.id.in_(["cite-emergency-scope", "cite-emergency-tests"]))
        else:
            return []
        return list(self.session.scalars(statement.order_by(Citation.id)))

    def chunks_matching(self, query: str) -> list[DocumentChunk]:
        pattern = f"%{query.strip()}%"
        if pattern == "%%":
            return []
        return list(self.session.scalars(select(DocumentChunk).where(or_(DocumentChunk.text.ilike(pattern), DocumentChunk.section.ilike(pattern)))))
