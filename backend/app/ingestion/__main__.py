from __future__ import annotations

import argparse
import json

from ..database import SessionLocal
from ..config import settings
from ..services.embeddings import provider_from_settings
from .pipeline import embed_document_chunks, ingest_electric_kettle


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest captured authoritative BIS records")
    parser.add_argument("target", choices=["standards", "qco", "labs", "electric-kettle", "embeddings"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-model-download", action="store_true", help="Permit the explicit embeddings command to download its configured local model")
    args = parser.parse_args()
    # Vertical sub-targets intentionally run the same atomic graph ingest so no partial
    # canonical regulatory state is exposed.
    with SessionLocal() as session:
        if args.target == "embeddings":
            result = embed_document_chunks(session, provider_from_settings(settings.embedding_provider, allow_download=args.allow_model_download))
        else:
            result = ingest_electric_kettle(session, dry_run=args.dry_run)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
