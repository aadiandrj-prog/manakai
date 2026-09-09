"""Compatibility entry point for the declarative product-family classifier."""
from ..coverage_registry import classify_from_registry


def classify_authoritative(description: str) -> dict:
    return classify_from_registry(description)
