from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from ..db_models import DocumentChunk
from ..repositories.documents import DocumentRepository
from .embeddings import EmbeddingProvider


@dataclass(frozen=True)
class RankedEvidence:
    chunk: DocumentChunk
    score: float
    reasons: tuple[str, ...]


class HybridRetrievalService:
    def __init__(self, session: Session, embedding_provider: EmbeddingProvider):
        self.documents = DocumentRepository(session)
        self.embedding_provider = embedding_provider

    def search(self, query: str, *, limit: int = 8) -> list[RankedEvidence]:
        lexical = self.documents.lexical_chunks(query, limit=30)
        metadata = self.documents.metadata_chunks(query, limit=30)
        vectors = self.embedding_provider.embed([query])
        semantic = self.documents.vector_chunks(vectors[0], limit=30) if vectors else []
        scores: dict[str, float] = {}
        reasons: dict[str, set[str]] = {}
        chunks: dict[str, DocumentChunk] = {}
        for chunk in metadata:
            scores[chunk.id] = 2.0
            reasons.setdefault(chunk.id, set()).add("metadata")
            chunks[chunk.id] = chunk
        for rank, (chunk, _) in enumerate(lexical, start=1):
            scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (60 + rank)
            reasons.setdefault(chunk.id, set()).add("lexical")
            chunks[chunk.id] = chunk
        for rank, (chunk, _) in enumerate(semantic, start=1):
            scores[chunk.id] = scores.get(chunk.id, 0) + 0.8 / (60 + rank)
            reasons.setdefault(chunk.id, set()).add("vector")
            chunks[chunk.id] = chunk
        normalized_query = re.sub(r"\s+", " ", query.casefold())
        identifiers = re.findall(r"(?:is\s*)?\d+(?:\s*\([^)]*\))?(?:\s*[:/-]\s*\d+)*", normalized_query)
        clauses = re.findall(r"(?:clause|cl\.?)[ ]*([a-z0-9.()-]+)", normalized_query)
        for chunk_id, chunk in chunks.items():
            haystack = f"{chunk.document_id} {chunk.section or ''} {chunk.text}".casefold()
            if any(identifier.strip() in haystack for identifier in identifiers):
                scores[chunk_id] += 1.0
                reasons[chunk_id].add("exact-identifier")
            if chunk.clause and any(value == chunk.clause.casefold() for value in clauses):
                scores[chunk_id] += 1.0
                reasons[chunk_id].add("exact-clause")
        return [RankedEvidence(chunks[item_id], score, tuple(sorted(reasons[item_id]))) for item_id, score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:limit]]
