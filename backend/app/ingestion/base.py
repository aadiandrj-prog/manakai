from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from hashlib import sha256
from html.parser import HTMLParser
import re
from typing import Any
import unicodedata
from urllib.parse import urlparse

import httpx


ALLOWED_HOSTS = {
    "www.bis.gov.in",
    "bis.gov.in",
    "www.services.bis.gov.in",
    "services.bis.gov.in",
    "lims.bis.gov.in",
    "www.dpiit.gov.in",
    "dpiit.gov.in",
}


class SourceSecurityError(ValueError):
    pass


@dataclass(frozen=True)
class FetchedSource:
    url: str
    content: bytes
    content_type: str

    @property
    def content_hash(self) -> str:
        return sha256(self.content).hexdigest()


SOURCE_FINGERPRINT_VERSION = "semantic-text-v1"


class _VisibleTextParser(HTMLParser):
    """Extract visible text while ignoring volatile page machinery."""

    _ignored_tags = {"script", "style", "noscript", "template", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in self._ignored_tags:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._ignored_tags and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)


def source_fingerprint(source: FetchedSource) -> str:
    """Hash stable source content, not HTML tokens, scripts, or formatting bytes."""
    content_type = source.content_type.lower()
    if "html" in content_type or source.content.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        parser = _VisibleTextParser()
        parser.feed(source.content.decode("utf-8", errors="replace"))
        text = " ".join(parser.parts)
        normalized = unicodedata.normalize("NFKC", text)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return sha256(normalized.encode("utf-8")).hexdigest()
    return source.content_hash


class BISSourceAdapter(ABC):
    """Fetch → parse → normalize → validate contract, independent of persistence."""

    name = "bis-source"
    max_document_bytes = 12 * 1024 * 1024

    async def fetch(self, url: str) -> FetchedSource:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password:
            raise SourceSecurityError("Only allow-listed BIS/DPIIT HTTPS URLs may be ingested")
        timeout = httpx.Timeout(20.0, connect=8.0)
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                    async with client.stream("GET", url, headers={"User-Agent": "ManakAI-BIS-Ingestion/0.3"}) as response:
                        response.raise_for_status()
                        final = urlparse(str(response.url))
                        if final.scheme != "https" or final.hostname not in ALLOWED_HOSTS:
                            raise SourceSecurityError("Source redirected outside the BIS/DPIIT allow-list")
                        size_header = response.headers.get("content-length")
                        if size_header and int(size_header) > self.max_document_bytes:
                            raise SourceSecurityError("Source document exceeds the configured size limit")
                        chunks: list[bytes] = []
                        size = 0
                        async for chunk in response.aiter_bytes():
                            size += len(chunk)
                            if size > self.max_document_bytes:
                                raise SourceSecurityError("Source document exceeds the configured size limit")
                            chunks.append(chunk)
                return FetchedSource(
                    url=url,
                    content=b"".join(chunks),
                    content_type=response.headers.get("content-type", ""),
                )
            except httpx.HTTPStatusError as exc:
                if attempt == 2 or exc.response.status_code not in {429, 500, 502, 503, 504}:
                    raise
            except httpx.TransportError:
                if attempt == 2:
                    raise
            await asyncio.sleep(0.25 * (2**attempt))
        raise RuntimeError("unreachable")

    @abstractmethod
    def parse(self, raw: Any) -> Any: ...

    @abstractmethod
    def normalize(self, parsed: Any) -> list[dict[str, Any]]: ...

    @abstractmethod
    def validate(self, records: list[dict[str, Any]]) -> list[str]: ...

    def provenance(self, record: dict[str, Any]) -> dict[str, Any]:
        source = record["source_record"]
        return {
            "source_url": source["source_url"],
            "source_authority": source["source_authority"],
            "source_type": source["source_type"],
            "document_identifier": source.get("document_identifier"),
            "content_hash": source["content_hash"],
            "verification_status": "AUTHORITATIVE",
        }


def stable_hash(value: Any) -> str:
    import json

    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(payload.encode("utf-8")).hexdigest()
