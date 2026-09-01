"""BIS ingestion adapters and command-line entry point."""

from .pipeline import ingest_electric_kettle

__all__ = ["ingest_electric_kettle"]
