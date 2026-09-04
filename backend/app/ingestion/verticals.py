from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import db_models as m
from .adapters import BISHallmarkingAdapter, BISVerticalAdapter
from .pipeline import _date, _link, _source, _upsert, ingest_electric_kettle


FIXTURE_PATH = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "official" / "multi_vertical.json"


def load_vertical_fixture(path: Path = FIXTURE_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_payload(url: str, source_type: str, identifier: str, *, published_at: str | None = None, standard: dict | None = None) -> dict:
    payload = {
        "source_url": url, "source_authority": "Bureau of Indian Standards", "source_type": source_type,
        "document_identifier": identifier, "published_at": published_at, "effective_from": None, "effective_until": None,
        "standard_number": standard.get("number") if standard else None,
        "standard_year": int(standard["version"]) if standard and str(standard.get("version", "")).isdigit() else None,
    }
    # One captured URL is one source snapshot even when it supports multiple
    # normalised records (for example the Scheme I product list).
    payload["content_hash"] = hashlib.sha256(url.encode()).hexdigest()
    return payload


def _captured_source(session: Session, payload: dict, run_id: str, retrieved_at: datetime) -> m.SourceRecord:
    # The same official index can support several product records. Reuse the
    # already-captured page instead of misclassifying those uses as a live change.
    existing = session.scalar(select(m.SourceRecord).where(m.SourceRecord.source_url == payload["source_url"]).order_by(m.SourceRecord.retrieved_at.desc()))
    return existing or _source(session, payload, run_id, retrieved_at)


def _regime(session: Session, kind: str, source_id: str) -> m.RegulatoryRegime:
    if kind == "HALLMARKING":
        values = {"slug": "bis-hallmarking", "name": "BIS Hallmarking", "regime_type": "HALLMARKING",
                  "description": "Registration, assaying and hallmarking regime for precious-metal articles.", "source_kind": "AUTHORITATIVE", "source_record_id": source_id,
                  "journey_template": ["Article classified", "Fineness grade checked", "Mandatory district/order checked", "Registered jeweller route", "Assaying and Hallmarking Centre", "HUID verified in BIS Care"]}
        item, _ = _upsert(session, m.RegulatoryRegime, "regime-hallmarking", values)
        return item
    values = {"slug": "scheme-i-product-certification", "name": "Scheme I Product Certification", "regime_type": "PRODUCT_CERTIFICATION",
              "description": "BIS Standard Mark licensing under Scheme I where the applicable QCO requires it.", "source_kind": "AUTHORITATIVE", "source_record_id": source_id,
              "journey_template": ["Product classified", "Applicable standard identified", "QCO status checked", "Scheme I identified", "Product manual reviewed", "Testing scope selected", "Recognised laboratory checked", "Application prepared"]}
    item, _ = _upsert(session, m.RegulatoryRegime, "regime-scheme-i", values)
    return item


def ensure_kettle_coverage(session: Session) -> None:
    standard = session.get(m.Standard, "is-302-2-15-auth")
    category = session.get(m.ProductCategory, "category-heating-liquids")
    source = session.get(m.SourceRecord, "src-" + "")
    if not standard or not category:
        return
    source_link = session.query(m.ProvenanceLink).filter_by(record_type="product_category", record_id="product-electric-kettle").first()
    source_id = source_link.source_record_id if source_link else session.query(m.SourceRecord.id).filter(m.SourceRecord.standard_number == standard.number).scalar()
    if not source_id:
        return
    regime = _regime(session, "PRODUCT_CERTIFICATION", source_id)
    _upsert(session, m.CoverageRecord, "coverage-electric-kettle", {
        "product_category_id": category.id, "primary_standard_id": standard.id, "regime_id": regime.id,
        "coverage_status": "VERIFIED", "coverage_reason": "The electric-kettle vertical has authoritative BIS standard, QCO, product-manual and LIMS provenance.",
        "verified_at": datetime.now(timezone.utc), "authoritative_sources_count": 5,
        "known_limitations": ["Rated voltage is required to conclusively evaluate the QCO voltage scope."],
        "standard_metadata_available": True, "compliance_verified": True,
        "metadata_json": {"required_documents": ["Model/type, rating and capacity declaration", "Construction and protection-class details", "Instruction manual and photographs"]},
    })


def ingest_vertical(session: Session, key: str, *, dry_run: bool = False, fixture_path: Path = FIXTURE_PATH) -> dict:
    fixture = load_vertical_fixture(fixture_path)
    raw = next((item for item in fixture["verticals"] if item["key"] == key), None)
    if raw is None:
        raise ValueError(f"Unknown authoritative vertical: {key}")
    adapter = BISVerticalAdapter()
    errors = adapter.validate(adapter.normalize(adapter.parse(raw)))
    if errors:
        raise ValueError("; ".join(errors))
    run = m.IngestionRun(id=str(uuid4()), adapter=key, status="RUNNING", started_at=datetime.now(timezone.utc))
    session.add(run); session.commit()
    retrieved_at = datetime.now(timezone.utc); created = updated = 0
    try:
        with session.begin_nested():
            standard = raw["standard"]
            std_src = _captured_source(session, _source_payload(raw["standard_source"], "BIS_STANDARD_METADATA", f"{standard['number']}:{standard['version']}", published_at=standard.get("publication_date"), standard=standard), run.id, retrieved_at)
            values = {k: standard[k] for k in ("number", "title", "version", "status", "category", "scope")}
            values.update(publication_date=_date(standard.get("publication_date")), source_kind="AUTHORITATIVE", retrieved_at=retrieved_at)
            _, made = _upsert(session, m.Standard, standard["id"], values); created += made; updated += not made
            _link(session, "standard", standard["id"], std_src.id, "Official BIS standard metadata")
            for related in raw.get("related_standards", []):
                related_values = {k: related[k] for k in ("number", "title", "version", "status", "category", "scope")}
                related_values.update(source_kind="AUTHORITATIVE", retrieved_at=retrieved_at)
                _, made = _upsert(session, m.Standard, related["id"], related_values); created += made; updated += not made
                _, made = _upsert(session, m.StandardRelationship, f"rel-{key}-{related['id']}", {"source_standard_id": standard["id"], "target_standard_id": related["id"], "relationship_type": "TESTED_USING", "rationale": "The official product manual identifies this separate test-method standard.", "source_record_id": std_src.id}); created += made; updated += not made
            previous_standard_id = None
            for historical in raw.get("historical_standards", []):
                hist_values = {"number": historical["number"], "title": historical["title"], "version": historical["version"], "status": historical["status"], "category": standard["category"], "scope": standard["scope"], "publication_date": _date(historical.get("publication_date")), "superseded_by_id": standard["id"], "source_kind": "AUTHORITATIVE", "retrieved_at": retrieved_at}
                _, made = _upsert(session, m.Standard, historical["id"], hist_values); created += made; updated += not made; previous_standard_id = historical["id"]

            category = raw["category"]
            _, made = _upsert(session, m.ProductCategory, category["id"], {"slug": category["slug"], "name": category["name"], "source_kind": "AUTHORITATIVE"}); created += made; updated += not made
            _, made = _upsert(session, m.ProductStandardMapping, f"mapping-{key}", {"product_category_id": category["id"], "standard_id": standard["id"], "relationship_type": "GOVERNED_BY", "rationale": "Official BIS product title and product manual establish this product-standard relationship.", "source_record_id": std_src.id}); created += made; updated += not made

            qco = raw["qco"]
            qco_src = _captured_source(session, _source_payload(qco["url"], "GOVERNMENT_QCO", qco["notification_number"], published_at=qco["notification_date"], standard=standard), run.id, retrieved_at)
            _, made = _upsert(session, m.QCO, qco["id"], {"title": qco["title"], "status": qco["status"], "publication_date": _date(qco["notification_date"]), "notification_number": qco["notification_number"], "notification_date": _date(qco["notification_date"]), "effective_date": _date(qco["effective_date"]), "source_verified": True, "source_kind": "AUTHORITATIVE", "source_url": qco["url"], "source_record_id": qco_src.id}); created += made; updated += not made
            _, made = _upsert(session, m.QCOApplicability, f"qco-app-{key}", {"qco_id": qco["id"], "enterprise_category": "GENERAL", "covered_product_category": category["slug"], "standard_reference": f"{standard['number']}:{standard['version']}", "effective_from": _date(qco["effective_date"]), "source_record_id": qco_src.id}); created += made; updated += not made
            _, made = _upsert(session, m.StandardQCO, f"sqco-{key}", {"standard_id": standard["id"], "qco_id": qco["id"]}); created += made; updated += not made
            regime = _regime(session, "PRODUCT_CERTIFICATION", qco_src.id)
            _, made = _upsert(session, m.CertificationScheme, f"scheme-i-{key}", {"standard_id": standard["id"], "name": "Scheme I (ISI Mark Scheme)", "description": "BIS Standard Mark licence under Scheme I.", "source_kind": "AUTHORITATIVE", "qco_id": qco["id"], "source_record_id": qco_src.id}); created += made; updated += not made

            manuals = [*raw.get("historical_manuals", []), raw["manual"]]
            prior_manual_id = None
            for manual in manuals:
                manual_src = _captured_source(session, _source_payload(manual["url"], "BIS_PRODUCT_MANUAL", manual["identifier"], published_at=manual["published_at"], standard=standard), run.id, retrieved_at)
                document_id = f"doc-{manual['id']}"
                _, made = _upsert(session, m.Document, document_id, {"title": manual["identifier"], "document_type": "BIS_PRODUCT_MANUAL", "standard_id": standard["id"], "version": manual["published_at"], "source_url": manual["url"], "publication_date": _date(manual["published_at"]), "retrieved_at": retrieved_at, "source_kind": "AUTHORITATIVE", "source_authority": "Bureau of Indian Standards", "verification_status": "AUTHORITATIVE", "document_identifier": manual["identifier"], "content_hash": manual_src.content_hash, "status": manual["status"]}); created += made; updated += not made
                _, made = _upsert(session, m.DocumentChunk, f"chunk-{manual['id']}", {"document_id": document_id, "page": 1, "clause": "Scope", "section": "Product manual metadata", "heading": manual["identifier"], "paragraph_index": 1, "text": f"Official BIS product manual {manual['identifier']} for {standard['number']}:{standard['version']}. Current status: {manual['status']}.", "content_hash": hashlib.sha256(manual["identifier"].encode()).hexdigest()}); created += made; updated += not made
                _, made = _upsert(session, m.ProductManual, manual["id"], {"standard_id": standard["id"], "document_id": document_id, "source_kind": "AUTHORITATIVE", "manual_identifier": manual["identifier"], "status": manual["status"], "source_record_id": manual_src.id, "supersedes_id": prior_manual_id}); created += made; updated += not made
                if prior_manual_id:
                    session.get(m.ProductManual, prior_manual_id).superseded_by_id = manual["id"]
                prior_manual_id = manual["id"]

            lims_src = _captured_source(session, _source_payload(raw["lims_url"], "BIS_LIMS_SCOPE", f"LIMS scope for {standard['number']}", standard=standard), run.id, retrieved_at)
            for clause, name in raw["tests"]:
                test_id = f"test-{key}-{str(clause).replace('.', '-')}"
                _, made = _upsert(session, m.Test, test_id, {"standard_id": standard["id"], "name": name, "clause": str(clause), "source_kind": "AUTHORITATIVE", "source_record_id": lims_src.id}); created += made; updated += not made
                for link in [item for item in raw.get("test_standard_links", []) if str(item["clause"]) == str(clause)]:
                    _, made = _upsert(session, m.TestStandardRelationship, f"test-link-{test_id}-{link['standard_id']}"[:64], {"test_id": test_id, "referenced_standard_id": link["standard_id"], "relationship_type": "TEST_METHOD_FROM", "rationale": "Separate test-method standard explicitly referenced by the BIS product manual.", "source_record_id": lims_src.id}); created += made; updated += not made
            for lab in raw["labs"]:
                _, made = _upsert(session, m.Laboratory, lab["id"], {"name": lab["name"], "city": lab.get("city"), "state": lab.get("state"), "address": lab.get("address"), "source_kind": "AUTHORITATIVE"}); created += made; updated += not made
                valid_until = _date(lab.get("valid_until")); status = "RECOGNISED" if valid_until else "UNKNOWN"
                _, made = _upsert(session, m.LaboratoryRecognition, f"rec-{lab['id']}-{key}", {"laboratory_id": lab["id"], "standard_id": standard["id"], "valid_from": _date(lab.get("valid_from")), "valid_until": valid_until, "capabilities": [lab["scope"]], "source_kind": "AUTHORITATIVE", "scope_identifier": lab["scope_identifier"], "scope": lab["scope"], "test_clauses": [str(item[0]) for item in raw["tests"]], "status": status, "source_url": raw["lims_url"], "retrieved_at": retrieved_at, "verification_status": "AUTHORITATIVE", "source_record_id": lims_src.id, "grade_type": lab.get("scope"), "testing_charge": lab.get("testing_charge"), "remark": lab.get("remark"), "completeness_warning": lab.get("warning")}); created += made; updated += not made

            coverage = raw["coverage"]
            _, made = _upsert(session, m.CoverageRecord, f"coverage-{key}", {"product_category_id": category["id"], "primary_standard_id": standard["id"], "regime_id": regime.id, "coverage_status": coverage["status"], "coverage_reason": coverage["reason"], "verified_at": retrieved_at, "authoritative_sources_count": coverage["sources"], "known_limitations": coverage["limitations"], "standard_metadata_available": True, "compliance_verified": coverage["status"] == "VERIFIED", "metadata_json": {"required_documents": raw["required_documents"], "manual_id": raw["manual"]["id"], "evidence": [[f"doc-{raw['manual']['id']}", f"chunk-{raw['manual']['id']}", f"Official BIS product manual for {standard['number']}:{standard['version']}"]]}}); created += made; updated += not made
            if dry_run:
                raise RuntimeError("DRY_RUN")
        run.status = "SUCCESS"
    except RuntimeError as exc:
        if str(exc) != "DRY_RUN":
            raise
        run.status = "SUCCESS"; created = updated = 0
    except Exception as exc:
        session.rollback(); run = session.get(m.IngestionRun, run.id); run.status = "FAILED"; run.errors = [str(exc)]; run.records_rejected = 1; run.finished_at = datetime.now(timezone.utc); session.commit(); raise
    run.records_fetched = 1 + len(raw["tests"]) + len(raw["labs"]); run.records_created = created; run.records_updated = updated; run.finished_at = datetime.now(timezone.utc); session.commit()
    return {"run_id": run.id, "adapter": key, "status": run.status, "records_created": created, "records_updated": updated, "dry_run": dry_run}


def ingest_hallmarking(session: Session, *, dry_run: bool = False, fixture_path: Path = FIXTURE_PATH) -> dict:
    fixture = load_vertical_fixture(fixture_path); adapter = BISHallmarkingAdapter(); raw = adapter.normalize(adapter.parse(fixture))[0]
    errors = adapter.validate([raw])
    if errors: raise ValueError("; ".join(errors))
    run = m.IngestionRun(id=str(uuid4()), adapter="hallmarking", status="RUNNING", started_at=datetime.now(timezone.utc)); session.add(run); session.commit()
    retrieved_at = datetime.now(timezone.utc); created = updated = 0
    try:
        with session.begin_nested():
            standard = raw["standard"]
            source = _captured_source(session, _source_payload(raw["standard_source"], "BIS_HALLMARKING_GUIDANCE", f"{standard['number']}:{standard['version']}", published_at=standard["publication_date"], standard=standard), run.id, retrieved_at)
            _, made = _upsert(session, m.Standard, standard["id"], {**{k: standard[k] for k in ("number", "title", "version", "status", "category", "scope")}, "publication_date": _date(standard["publication_date"]), "source_kind": "AUTHORITATIVE", "retrieved_at": retrieved_at}); created += made; updated += not made
            category = raw["category"]; _, made = _upsert(session, m.ProductCategory, category["id"], {"slug": category["slug"], "name": category["name"], "source_kind": "AUTHORITATIVE"}); created += made; updated += not made
            _, made = _upsert(session, m.ProductStandardMapping, "mapping-gold-hallmarking", {"product_category_id": category["id"], "standard_id": standard["id"], "relationship_type": "FINENESS_AND_MARKING_STANDARD", "rationale": "Official BIS hallmarking FAQ identifies IS 1417:2016 and permitted fineness grades.", "source_record_id": source.id}); created += made; updated += not made
            orders = [*raw.get("order_history", []), raw["order"]]
            prior_order_id = None; order_src = None
            for order in orders:
                order_src = _captured_source(session, _source_payload(order["url"], "GOVERNMENT_HALLMARKING_ORDER", order["notification_number"], published_at=order["notification_date"], standard=standard), run.id, retrieved_at)
                _, made = _upsert(session, m.QCO, order["id"], {"title": order["title"], "status": order["status"], "publication_date": _date(order["notification_date"]), "notification_number": order["notification_number"], "notification_date": _date(order["notification_date"]), "effective_date": _date(order["effective_date"]), "source_verified": True, "source_kind": "AUTHORITATIVE", "source_url": order["url"], "source_record_id": order_src.id, "supersedes_id": prior_order_id}); created += made; updated += not made
                if prior_order_id: session.get(m.QCO, prior_order_id).superseded_by_id = order["id"]
                _, made = _upsert(session, m.QCOApplicability, f"qco-app-{order['id']}", {"qco_id": order["id"], "enterprise_category": "GENERAL", "covered_product_category": category["slug"], "standard_reference": "IS 1417:2016", "effective_from": _date(order["effective_date"]), "source_record_id": order_src.id}); created += made; updated += not made
                _, made = _upsert(session, m.StandardQCO, f"sqco-{order['id']}", {"standard_id": standard["id"], "qco_id": order["id"]}); created += made; updated += not made
                prior_order_id = order["id"]
            regime = _regime(session, "HALLMARKING", order_src.id); coverage = raw["coverage"]
            _, made = _upsert(session, m.CoverageRecord, "coverage-gold-jewellery", {"product_category_id": category["id"], "primary_standard_id": standard["id"], "regime_id": regime.id, "coverage_status": coverage["status"], "coverage_reason": coverage["reason"], "verified_at": retrieved_at, "authoritative_sources_count": coverage["sources"], "known_limitations": coverage["limitations"], "standard_metadata_available": True, "compliance_verified": False, "metadata_json": {"fineness": raw["fineness"], "official_ahc_directory": raw["official_ahc_directory"], "required_documents": ["Registered jeweller details", "Article description and declared fineness", "HUID and hallmark elements"]}}); created += made; updated += not made
            for guide in raw["guidance"]:
                guide_src = _captured_source(session, _source_payload(guide["source_url"], "BIS_HALLMARKING_GUIDANCE", guide["title"], standard=standard), run.id, retrieved_at)
                _, made = _upsert(session, m.HallmarkingGuidance, f"guidance-{guide['topic']}", {"topic": guide["topic"], "title": guide["title"], "guidance": guide["steps"], "source_url": guide["source_url"], "source_kind": "AUTHORITATIVE", "source_record_id": guide_src.id}); created += made; updated += not made
                document_id = f"doc-hallmarking-{guide['topic']}"; text = " ".join(guide["steps"])
                _, made = _upsert(session, m.Document, document_id, {"title": guide["title"], "document_type": "BIS_HALLMARKING_GUIDANCE", "standard_id": standard["id"], "source_url": guide["source_url"], "retrieved_at": retrieved_at, "source_kind": "AUTHORITATIVE", "source_authority": "Bureau of Indian Standards", "verification_status": "AUTHORITATIVE", "document_identifier": guide["title"], "content_hash": hashlib.sha256(text.encode()).hexdigest(), "status": "ACTIVE"}); created += made; updated += not made
                _, made = _upsert(session, m.DocumentChunk, f"chunk-hallmarking-{guide['topic']}", {"document_id": document_id, "page": 1, "clause": None, "section": guide["title"], "heading": guide["title"], "paragraph_index": 1, "text": text, "content_hash": hashlib.sha256(text.encode()).hexdigest()}); created += made; updated += not made
            if dry_run: raise RuntimeError("DRY_RUN")
        run.status = "SUCCESS"
    except RuntimeError as exc:
        if str(exc) != "DRY_RUN": raise
        run.status = "SUCCESS"; created = updated = 0
    except Exception as exc:
        session.rollback(); run = session.get(m.IngestionRun, run.id); run.status = "FAILED"; run.errors = [str(exc)]; run.finished_at = datetime.now(timezone.utc); session.commit(); raise
    run.records_fetched = len(raw["guidance"]) + 3; run.records_created = created; run.records_updated = updated; run.finished_at = datetime.now(timezone.utc); session.commit()
    return {"run_id": run.id, "adapter": "hallmarking", "status": run.status, "records_created": created, "records_updated": updated, "dry_run": dry_run}


def ingest_all_authoritative(session: Session, *, dry_run: bool = False) -> dict:
    results = []; errors = []
    try:
        results.append({"adapter": "electric-kettle", **ingest_electric_kettle(session, dry_run=dry_run)})
        if not dry_run:
            ensure_kettle_coverage(session); session.commit()
    except Exception as exc:
        errors.append({"adapter": "electric-kettle", "error": str(exc)})
    for key in ("motorcycle-helmet", "ordinary-portland-cement", "domestic-pressure-cooker"):
        try: results.append(ingest_vertical(session, key, dry_run=dry_run))
        except Exception as exc: errors.append({"adapter": key, "error": str(exc)})
    try: results.append(ingest_hallmarking(session, dry_run=dry_run))
    except Exception as exc: errors.append({"adapter": "hallmarking", "error": str(exc)})
    return {"status": "SUCCESS" if not errors else "PARTIAL", "verticals": results, "errors": errors, "changes_review_required": 0}
