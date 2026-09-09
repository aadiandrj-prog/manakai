from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse


SOURCE_REGISTRY_PATH = Path(__file__).resolve().parent / "data" / "source_registry.json"


@lru_cache(maxsize=1)
def load_source_registry() -> dict:
    payload = json.loads(SOURCE_REGISTRY_PATH.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("Unsupported source-registry schema")
    return payload


def validate_official_source_url(url: str) -> None:
    parsed = urlparse(url)
    allowed = {host for authority in load_source_registry()["authorities"] for host in authority["allowed_hosts"]}
    if parsed.scheme != "https" or parsed.hostname not in allowed or parsed.username or parsed.password:
        raise ValueError(f"Source URL is outside the approved official registry: {url}")
