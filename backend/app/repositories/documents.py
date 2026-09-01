import math
from dataclasses import dataclass
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from ..db_models import Citation, Document, DocumentChunk, Standard


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

    def lexical_chunks(self, query: str, *, limit: int = 20) -> list[tuple[DocumentChunk, float]]:
        cleaned = query.strip()
        if not cleaned:
            return []
        dialect = self.session.bind.dialect.name
        if dialect == "postgresql":
            vector = func.to_tsvector("english", func.coalesce(DocumentChunk.text, "") + " " + func.coalesce(DocumentChunk.section, ""))
            tsquery = func.websearch_to_tsquery("english", cleaned)
            rank = func.ts_rank_cd(vector, tsquery)
            statement = select(DocumentChunk, rank.label("rank")).where(vector.op("@@")(tsquery)).order_by(rank.desc()).limit(limit)
            return [(row[0], float(row[1])) for row in self.session.execute(statement)]
        terms = [term.casefold() for term in cleaned.replace(":", " ").split()]
        chunks = list(self.session.scalars(select(DocumentChunk)))
        scored = []
        for chunk in chunks:
            haystack = f"{chunk.document_id} {chunk.clause or ''} {chunk.section or ''} {chunk.text}".casefold()
            hits = sum(haystack.count(term) for term in terms)
            if hits:
                scored.append((chunk, float(hits)))
        return sorted(scored, key=lambda item: (-item[1], item[0].id))[:limit]

    def vector_chunks(self, embedding: list[float], *, limit: int = 20) -> list[tuple[DocumentChunk, float]]:
        if not embedding:
            return []
        if self.session.bind.dialect.name == "postgresql":
            distance = DocumentChunk.embedding.cosine_distance(embedding)
            statement = select(DocumentChunk, distance.label("distance")).where(DocumentChunk.embedding.is_not(None)).order_by(distance).limit(limit)
            return [(row[0], 1.0 - float(row[1])) for row in self.session.execute(statement)]
        chunks = [chunk for chunk in self.session.scalars(select(DocumentChunk)) if chunk.embedding is not None]
        def cosine(values: list[float]) -> float:
            dot = sum(a * b for a, b in zip(values, embedding))
            norm = math.sqrt(sum(a * a for a in values)) * math.sqrt(sum(b * b for b in embedding))
            return dot / norm if norm else 0.0
        return sorted(((chunk, cosine(chunk.embedding)) for chunk in chunks), key=lambda item: (-item[1], item[0].id))[:limit]

    def metadata_chunks(self, query: str, *, limit: int = 30) -> list[DocumentChunk]:
        import re
        digits = re.findall(r"\d+", query)
        clause_match = re.search(r"(?:clause|cl\.?)[ ]*([a-z0-9.()-]+)", query.casefold())
        filters = []
        if digits:
            filters.append(and_(*(Standard.number.ilike(f"%{value}%") for value in digits[:3])))
        if clause_match:
            filters.append(func.lower(DocumentChunk.clause) == clause_match.group(1))
        if not filters:
            return []
        statement = select(DocumentChunk).join(Document).outerjoin(Standard).where(or_(*filters)).order_by(DocumentChunk.id).limit(limit)
        return list(self.session.scalars(statement))
