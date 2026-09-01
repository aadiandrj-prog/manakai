from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class ClauseChunk:
    page: int | None
    heading: str | None
    clause: str | None
    subclause: str | None
    table_label: str | None
    paragraph_index: int
    text: str
    content_hash: str


class ClauseAwareParser:
    """Converts captured structural PDF output into clause-boundary chunks."""

    def parse_pages(self, pages: list[dict]) -> list[ClauseChunk]:
        chunks: list[ClauseChunk] = []
        for page in pages:
            page_heading = self._clean(page.get("heading"))
            for index, paragraph in enumerate(page.get("paragraphs", []), start=1):
                text = self._clean(paragraph.get("text"))
                if not text:
                    continue
                clause = self._clean(paragraph.get("clause"))
                chunks.append(ClauseChunk(
                    page=page.get("page"),
                    heading=self._clean(paragraph.get("heading")) or page_heading,
                    clause=clause,
                    subclause=clause if clause and "." in clause else None,
                    table_label=self._clean(paragraph.get("table")),
                    paragraph_index=index,
                    text=text,
                    content_hash=sha256(text.encode("utf-8")).hexdigest(),
                ))
        return chunks

    @staticmethod
    def _clean(value: object) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(str(value).replace("\x00", "").split())
        return cleaned or None
