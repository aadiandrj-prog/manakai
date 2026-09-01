from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    dimensions = 384

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class DisabledEmbeddingProvider(EmbeddingProvider):
    def embed(self, texts: list[str]) -> list[list[float]]:
        return []


class SentenceTransformerProvider(EmbeddingProvider):
    """Lazy optional provider; importing the app never downloads a model."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", *, local_files_only: bool = True):
        self.model_name = model_name
        self.local_files_only = local_files_only
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise RuntimeError("Install the optional sentence-transformers dependency to enable local embeddings") from exc
            self._model = SentenceTransformer(self.model_name, local_files_only=self.local_files_only)
            if self._model.get_sentence_embedding_dimension() != self.dimensions:
                raise RuntimeError(f"Embedding model must produce {self.dimensions} dimensions")
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._load().encode(texts, normalize_embeddings=True).tolist()


def provider_from_settings(name: str, *, allow_download: bool = False) -> EmbeddingProvider:
    if name == "sentence-transformers":
        return SentenceTransformerProvider(local_files_only=not allow_download)
    return DisabledEmbeddingProvider()
