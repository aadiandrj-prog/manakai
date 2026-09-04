from __future__ import annotations

import argparse
import asyncio
import json

from ..database import SessionLocal
from ..config import settings
from ..services.embeddings import provider_from_settings
from .pipeline import embed_document_chunks, ingest_electric_kettle
from .refresh import refresh_authoritative_sources
from .review import REVIEW_DECISIONS, resolve_review, review_report
from .verticals import ingest_all_authoritative, ingest_hallmarking, ingest_vertical


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest captured authoritative BIS records")
    parser.add_argument("target", choices=["standards", "qco", "labs", "electric-kettle", "helmets", "cement", "pressure-cookers", "hallmarking", "all-authoritative", "embeddings", "refresh", "review-report", "review-resolve"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--fail-on-change",
        action="store_true",
        help="Return a failing exit status when an authoritative source needs review",
    )
    parser.add_argument("--allow-model-download", action="store_true", help="Permit the explicit embeddings command to download its configured local model")
    parser.add_argument("--fail-on-pending", action="store_true", help="Return a failing exit status when source reviews remain pending")
    parser.add_argument("--event-id")
    parser.add_argument("--decision", choices=sorted(REVIEW_DECISIONS))
    parser.add_argument("--expected-new-hash")
    parser.add_argument("--reviewed-by")
    parser.add_argument("--review-note")
    parser.add_argument("--canonical-content-hash")
    args = parser.parse_args()
    # Vertical sub-targets intentionally run the same atomic graph ingest so no partial
    # canonical regulatory state is exposed.
    with SessionLocal() as session:
        if args.target == "review-report":
            result = review_report(session)
        elif args.target == "review-resolve":
            required = {
                "event-id": args.event_id,
                "decision": args.decision,
                "expected-new-hash": args.expected_new_hash,
                "reviewed-by": args.reviewed_by,
                "review-note": args.review_note,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                parser.error("review-resolve requires " + ", ".join(f"--{name}" for name in missing))
            result = resolve_review(
                session,
                event_id=args.event_id,
                decision=args.decision,
                expected_new_hash=args.expected_new_hash,
                reviewed_by=args.reviewed_by,
                review_note=args.review_note,
                canonical_content_hash=args.canonical_content_hash,
            )
        elif args.target == "embeddings":
            result = embed_document_chunks(session, provider_from_settings(settings.embedding_provider, allow_download=args.allow_model_download))
        elif args.target == "refresh":
            result = asyncio.run(refresh_authoritative_sources(session))
        elif args.target == "all-authoritative":
            result = ingest_all_authoritative(session, dry_run=args.dry_run)
        elif args.target == "helmets":
            result = ingest_vertical(session, "motorcycle-helmet", dry_run=args.dry_run)
        elif args.target == "cement":
            result = ingest_vertical(session, "ordinary-portland-cement", dry_run=args.dry_run)
        elif args.target == "pressure-cookers":
            result = ingest_vertical(session, "domestic-pressure-cooker", dry_run=args.dry_run)
        elif args.target == "hallmarking":
            result = ingest_hallmarking(session, dry_run=args.dry_run)
        else:
            result = ingest_electric_kettle(session, dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
    if args.fail_on_change and result.get("changes_review_required", 0):
        raise SystemExit(2)
    if args.fail_on_pending and result.get("pending_count", 0):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
