from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import db_models as m
from .coverage_registry import load_family_registry
from .ingestion.pipeline import _date, _upsert
from .ingestion.verticals import _captured_source, _regime, _source_payload
from .source_registry import validate_official_source_url


LIFECYCLE = ("DISCOVERED", "INGESTED", "AUTO_VALIDATED", "NEEDS_REVIEW", "APPROVED", "PUBLISHED", "REJECTED")
ALLOWED_TRANSITIONS = {
    "DISCOVERED": {"INGESTED", "REJECTED"}, "INGESTED": {"AUTO_VALIDATED", "NEEDS_REVIEW", "REJECTED"},
    "AUTO_VALIDATED": {"NEEDS_REVIEW", "REJECTED"}, "NEEDS_REVIEW": {"APPROVED", "REJECTED"},
    "APPROVED": {"PUBLISHED", "REJECTED"}, "PUBLISHED": {"NEEDS_REVIEW"}, "REJECTED": {"DISCOVERED"},
}


def coverage_score(family: dict) -> dict:
    checks = {
        "classification": bool(family.get("aliases") and family.get("product_type")),
        "standard_mapping": bool(family.get("standard") or family.get("existing")),
        "version_status": bool((family.get("standard") or {}).get("status") or family.get("existing")),
        "regulatory_regime": bool(family.get("qco") or family.get("existing")),
        "temporal_dates": bool((family.get("qco") or {}).get("effective_dates") or family.get("existing")),
        "scheme_evidence": bool(family.get("qco") or family.get("existing")),
        "product_manual": bool(family.get("manual") or family.get("existing")),
        "laboratory_relationship": bool(family.get("lims_url") or family.get("existing")),
        "citations": bool(family.get("standard_source") or family.get("existing")),
        "freshness_review": True,
    }
    passed = sum(checks.values())
    return {"score": passed * 10, "passed": passed, "total": len(checks), "checks": checks}


def transition_family(session: Session, slug: str, target: str, *, reviewer: str | None = None) -> m.ProductFamily:
    if target not in LIFECYCLE:
        raise ValueError(f"Unknown lifecycle status: {target}")
    family = session.scalar(select(m.ProductFamily).where(m.ProductFamily.slug == slug))
    if family is None:
        raise ValueError(f"Unknown product family: {slug}")
    if target not in ALLOWED_TRANSITIONS.get(family.lifecycle_status, set()):
        raise ValueError(f"Invalid transition: {family.lifecycle_status} -> {target}")
    now = datetime.now(timezone.utc)
    family.lifecycle_status = target
    if target == "APPROVED":
        if not reviewer:
            raise ValueError("A reviewer is required for approval")
        family.reviewed_by, family.reviewed_at = reviewer.strip(), now
    if target == "PUBLISHED":
        if not family.reviewed_at:
            raise ValueError("Only a reviewed family can be published")
        family.published_at = now
    coverage = session.scalar(select(m.CoverageRecord).join(m.ProductCategory).where(m.ProductCategory.slug == slug))
    if coverage:
        coverage.lifecycle_status = target
        coverage.reviewed_by, coverage.reviewed_at, coverage.published_at = family.reviewed_by, family.reviewed_at, family.published_at
    session.commit()
    return family


def ingest_family_registry(session: Session, *, publish_reviewed: bool = True, only_slug: str | None = None, dry_run: bool = False) -> dict:
    """Stage declarative records. Publication is allowed only for the reviewed bundled manifest."""
    run = m.IngestionRun(id=f"family-registry-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}", adapter="product-family-registry", status="RUNNING", started_at=datetime.now(timezone.utc))
    session.add(run); session.commit()
    created = updated = rejected = 0
    processed: list[str] = []
    try:
        with session.begin_nested():
            for config in load_family_registry():
                if only_slug and config["slug"] != only_slug:
                    continue
                made, changed = _ingest_one(session, config, run.id, publish_reviewed=publish_reviewed)
                created += made; updated += changed; processed.append(config["slug"])
            if only_slug and not processed:
                raise ValueError(f"Unknown product family: {only_slug}")
            if dry_run:
                raise RuntimeError("DRY_RUN")
        run.status = "SUCCESS"
    except RuntimeError as exc:
        if str(exc) != "DRY_RUN": raise
        run.status = "SUCCESS"; created = updated = 0
    except Exception as exc:
        session.rollback(); run = session.get(m.IngestionRun, run.id); run.status = "FAILED"; run.errors = [str(exc)]; rejected = 1; run.records_rejected = 1; run.finished_at = datetime.now(timezone.utc); session.commit(); raise
    run.records_fetched = len(processed); run.records_created = created; run.records_updated = updated; run.records_rejected = rejected; run.finished_at = datetime.now(timezone.utc); session.commit()
    return {"run_id": run.id, "status": run.status, "families": processed, "records_created": created, "records_updated": updated, "dry_run": dry_run}


def _ingest_one(session: Session, config: dict, run_id: str, *, publish_reviewed: bool) -> tuple[int, int]:
    now = datetime.now(timezone.utc); made_count = changed_count = 0
    for url in [config.get("standard_source"), config.get("lims_url"), (config.get("qco") or {}).get("url"), (config.get("manual") or {}).get("url")]:
        if url:
            validate_official_source_url(url)
    category = session.scalar(select(m.ProductCategory).where(m.ProductCategory.slug == config["slug"]))
    if category is None:
        category, made = _upsert(session, m.ProductCategory, f"category-{config['slug']}"[:64], {"slug": config["slug"], "name": config["name"], "source_kind": "AUTHORITATIVE"}); made_count += made; changed_count += not made
    existing_family = session.get(m.ProductFamily, f"family-{config['slug']}"[:64])
    preserve_publication = bool(existing_family and existing_family.lifecycle_status == "PUBLISHED" and not publish_reviewed)
    lifecycle = "PUBLISHED" if publish_reviewed or preserve_publication else "NEEDS_REVIEW"
    family_values = {"slug": config["slug"], "name": config["name"], "product_group": config["group"], "product_category_id": category.id, "aliases": config.get("aliases", []), "required_attributes": config.get("required_attributes", []), "optional_attributes": config.get("optional_attributes", []), "ambiguity_terms": config.get("ambiguity_terms", []), "lifecycle_status": lifecycle, "config_json": config, "reviewed_by": (existing_family.reviewed_by if preserve_publication else "Bundled manifest source review" if publish_reviewed else None), "reviewed_at": (existing_family.reviewed_at if preserve_publication else now if publish_reviewed else None), "published_at": (existing_family.published_at if preserve_publication else now if publish_reviewed else None)}
    family, made = _upsert(session, m.ProductFamily, f"family-{config['slug']}"[:64], family_values); made_count += made; changed_count += not made

    if config.get("existing"):
        coverage = session.scalar(select(m.CoverageRecord).join(m.ProductCategory).where(m.ProductCategory.slug == config["slug"]))
        if coverage:
            score = coverage_score(config); coverage.lifecycle_status = lifecycle; coverage.completeness_json = score; coverage.lab_completeness = "COMPLETE" if config["slug"] == "appliances-for-heating-liquids" else "SOURCE_SCOPED"; coverage.reviewed_by = family.reviewed_by; coverage.reviewed_at = family.reviewed_at; coverage.published_at = family.published_at; coverage.last_refreshed_at = now
            coverage.metadata_json = {**(coverage.metadata_json or {}), "product_group": config["group"], "aliases": config.get("aliases", [])}
        return made_count, changed_count

    standard = config["standard"]
    std_src = _captured_source(session, _source_payload(config["standard_source"], "BIS_STANDARD_METADATA", f"{standard['number']}:{standard['version']}", standard=standard), run_id, now)
    standard_record, made = _upsert(session, m.Standard, standard["id"], {"number": standard["number"], "title": standard["title"], "version": standard["version"], "status": standard["status"], "category": config["group"], "scope": standard["scope"], "source_kind": "AUTHORITATIVE", "retrieved_at": now}); made_count += made; changed_count += not made
    mapping, made = _upsert(session, m.ProductStandardMapping, f"mapping-{config['slug']}"[:64], {"product_category_id": category.id, "standard_id": standard_record.id, "relationship_type": "GOVERNED_BY", "rationale": "The official BIS product listing or product manual establishes this product-standard metadata relationship.", "source_record_id": std_src.id}); made_count += made; changed_count += not made
    _impact(session, std_src.id, family.id, "STANDARD_MAPPING", mapping.rationale)

    historical = config.get("historical_standard")
    if historical:
        _, made = _upsert(session, m.Standard, historical["id"], {"number": historical["number"], "title": historical["title"], "version": historical["version"], "status": historical["status"], "category": config["group"], "scope": historical["title"], "superseded_by_id": standard_record.id, "source_kind": "AUTHORITATIVE", "retrieved_at": now}); made_count += made; changed_count += not made

    qco = config.get("qco"); regime = None; qco_record = None
    if qco:
        qco_src = _captured_source(session, _source_payload(qco["url"], "GOVERNMENT_QCO", qco["notification_number"], published_at=qco["notification_date"], standard=standard), run_id, now)
        dates = qco["effective_dates"]
        qco_record, made = _upsert(session, m.QCO, qco["id"], {"title": qco["title"], "status": "NOTIFIED", "publication_date": _date(qco["notification_date"]), "notification_number": qco["notification_number"], "notification_date": _date(qco["notification_date"]), "effective_date": _date(dates["GENERAL"]), "source_verified": True, "source_kind": "AUTHORITATIVE", "source_url": qco["url"], "source_record_id": qco_src.id}); made_count += made; changed_count += not made
        if config.get("regulatory_conclusion", True):
            _, made = _upsert(session, m.StandardQCO, f"sqco-{config['slug']}"[:64], {"standard_id": standard_record.id, "qco_id": qco_record.id}); made_count += made; changed_count += not made
            for enterprise, effective in dates.items():
                _, made = _upsert(session, m.QCOApplicability, f"qco-app-{config['slug']}-{enterprise.lower()}"[:64], {"qco_id": qco_record.id, "enterprise_category": enterprise, "covered_product_category": config["slug"], "standard_reference": qco.get("standard_reference", f"{standard['number']}:{standard['version']}"), "effective_from": _date(effective), "source_record_id": qco_src.id}); made_count += made; changed_count += not made
            regime = _regime(session, "PRODUCT_CERTIFICATION", qco_src.id)
            _, made = _upsert(session, m.CertificationScheme, f"scheme-i-{config['slug']}"[:64], {"standard_id": standard_record.id, "name": "Scheme I (ISI Mark Scheme)", "description": "BIS Standard Mark licence under Scheme I where required by the cited QCO.", "source_kind": "AUTHORITATIVE", "qco_id": qco_record.id, "source_record_id": qco_src.id}); made_count += made; changed_count += not made
            _impact(session, qco_src.id, family.id, "REGULATORY_REQUIREMENT", f"{qco['notification_number']} and enterprise-specific effective dates")
        else:
            _impact(session, qco_src.id, family.id, "CONFLICT_REVIEW", f"{qco['notification_number']} cites {qco.get('standard_reference', 'a conflicting standard revision')}; no applicability edge was published")

    evidence = []
    manual = config.get("manual")
    if manual:
        manual_src = _captured_source(session, _source_payload(manual["url"], "BIS_PRODUCT_MANUAL", manual["identifier"], published_at=manual["published_at"], standard=standard), run_id, now)
        document_id = f"doc-{manual['id']}"[:64]; chunk_id = f"chunk-{manual['id']}"[:64]
        digest = hashlib.sha256(json.dumps({"family": config["slug"], "manual": manual}, sort_keys=True).encode()).hexdigest()
        _, made = _upsert(session, m.Document, document_id, {"title": manual["identifier"], "document_type": "BIS_PRODUCT_MANUAL", "standard_id": standard_record.id, "version": manual["published_at"], "source_url": manual["url"], "publication_date": _date(manual["published_at"]), "retrieved_at": now, "source_kind": "AUTHORITATIVE", "source_authority": "Bureau of Indian Standards", "verification_status": "AUTHORITATIVE", "document_identifier": manual["identifier"], "content_hash": digest, "status": "ACTIVE"}); made_count += made; changed_count += not made
        _, made = _upsert(session, m.DocumentChunk, chunk_id, {"document_id": document_id, "page": 1, "clause": "Metadata", "section": "Product manual metadata", "heading": manual["identifier"], "paragraph_index": 1, "text": f"The official BIS product-manual listing associates {standard['number']}:{standard['version']} with {config['name']}. This stored chunk is metadata, not reproduced standards content.", "content_hash": digest}); made_count += made; changed_count += not made
        _, made = _upsert(session, m.ProductManual, manual["id"], {"standard_id": standard_record.id, "document_id": document_id, "source_kind": "AUTHORITATIVE", "manual_identifier": manual["identifier"], "status": "ACTIVE", "source_record_id": manual_src.id}); made_count += made; changed_count += not made
        evidence.append([document_id, chunk_id, f"Official BIS product-manual metadata for {standard['number']}:{standard['version']}"])
        _impact(session, manual_src.id, family.id, "PRODUCT_MANUAL", manual["identifier"])
    if config.get("lims_url"):
        lims_src = _captured_source(session, _source_payload(config["lims_url"], "BIS_LIMS_SCOPE", f"LIMS query for {standard['number']}", standard=standard), run_id, now)
        _impact(session, lims_src.id, family.id, "LABORATORY_SCOPE", "Official BIS LIMS standard-scope query; individual validity is not inferred")

    score = coverage_score(config)
    status = config["coverage_status"]
    if status == "VERIFIED" and score["score"] < 100:
        status = "PARTIAL"
    coverage_values = {"product_category_id": category.id, "primary_standard_id": standard_record.id, "regime_id": regime.id if regime else None, "coverage_status": status, "coverage_reason": config["coverage_reason"], "verified_at": now if status == "VERIFIED" else None, "authoritative_sources_count": config.get("source_count", 1), "known_limitations": config.get("limitations", []), "standard_metadata_available": True, "compliance_verified": status == "VERIFIED", "lifecycle_status": lifecycle, "completeness_json": score, "lab_completeness": config.get("lab_completeness", "UNKNOWN"), "reviewed_by": family.reviewed_by, "reviewed_at": family.reviewed_at, "published_at": family.published_at, "last_refreshed_at": now, "metadata_json": {"manual_id": manual["id"] if manual else None, "required_documents": ["Product specification and declared ratings", "Model and construction details", "Applicable test records", "Marking and user instructions"], "evidence": evidence, "lims_url": config.get("lims_url"), "product_group": config["group"], "aliases": config.get("aliases", [])}}
    _, made = _upsert(session, m.CoverageRecord, f"coverage-{config['slug']}"[:64], coverage_values); made_count += made; changed_count += not made
    return made_count, changed_count


def _impact(session: Session, source_id: str, family_id: str, impact_type: str, note: str) -> None:
    digest = hashlib.sha256(f"{source_id}|{family_id}|{impact_type}".encode()).hexdigest()[:20]
    _upsert(session, m.SourceFamilyImpact, f"impact-{digest}", {"source_record_id": source_id, "product_family_id": family_id, "impact_type": impact_type, "relationship_note": note})
