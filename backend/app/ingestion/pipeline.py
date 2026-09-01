from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import db_models as m
from .adapters import (
    BISCompulsoryCertificationAdapter,
    BISLIMSAdapter,
    BISProductManualAdapter,
    BISQCOAdapter,
    BISStandardAdapter,
)
from .parser import ClauseAwareParser


FIXTURE_PATH = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "official" / "electric_kettle.json"


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def load_fixture(path: Path = FIXTURE_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _source(session: Session, payload: dict, run_id: str, retrieved_at: datetime) -> m.SourceRecord:
    existing = session.scalar(select(m.SourceRecord).where(
        m.SourceRecord.source_url == payload["source_url"],
        m.SourceRecord.content_hash == payload["content_hash"],
    ))
    if existing:
        return existing
    record = m.SourceRecord(
        id=f"src-{payload['content_hash'][:20]}",
        source_url=payload["source_url"],
        source_authority=payload["source_authority"],
        source_type=payload["source_type"],
        retrieved_at=retrieved_at,
        published_at=_date(payload.get("published_at")),
        effective_from=_date(payload.get("effective_from")),
        effective_until=_date(payload.get("effective_until")),
        document_identifier=payload.get("document_identifier"),
        content_hash=payload["content_hash"],
        ingestion_run_id=run_id,
        verification_status="AUTHORITATIVE",
        official_notification_number=payload.get("official_notification_number"),
        gazette_reference=payload.get("gazette_reference"),
        standard_number=payload.get("standard_number"),
        standard_year=payload.get("standard_year"),
        metadata_json={"capture": "sanitised official-source fixture"},
    )
    session.add(record)
    session.flush()
    return record


def _link(session: Session, record_type: str, record_id: str, source_id: str, claim: str) -> None:
    link_id = f"prov-{record_type[:12]}-{record_id}-{source_id[-8:]}"[:64]
    if session.get(m.ProvenanceLink, link_id) is None:
        session.add(m.ProvenanceLink(id=link_id, record_type=record_type, record_id=record_id, source_record_id=source_id, claim=claim))


def _upsert(session: Session, model, record_id: str, values: dict) -> tuple[object, bool]:
    item = session.get(model, record_id)
    created = item is None
    if created:
        item = model(id=record_id, **values)
        session.add(item)
    else:
        for key, value in values.items():
            setattr(item, key, value)
    session.flush()
    return item, created


def ingest_electric_kettle(session: Session, *, dry_run: bool = False, fixture_path: Path = FIXTURE_PATH) -> dict:
    """Atomically stages and commits the captured authoritative kettle vertical."""
    fixture = load_fixture(fixture_path)
    run = m.IngestionRun(id=str(uuid4()), adapter="electric-kettle", status="RUNNING", started_at=datetime.now(timezone.utc))
    session.add(run)
    session.commit()
    retrieved_at = datetime.now(timezone.utc)
    created = updated = rejected = 0
    try:
        adapters = [BISStandardAdapter(), BISProductManualAdapter(), BISQCOAdapter(), BISCompulsoryCertificationAdapter(), BISLIMSAdapter()]
        normalized: dict[str, list[dict]] = {}
        errors: list[str] = []
        for adapter in adapters:
            records = adapter.normalize(adapter.parse(fixture))
            normalized[adapter.name] = records
            errors.extend(f"{adapter.name}: {error}" for error in adapter.validate(records))
        run.records_fetched = sum(len(items) for items in normalized.values())
        if errors:
            raise ValueError("; ".join(errors))

        with session.begin_nested():
            source_by_url: dict[str, m.SourceRecord] = {}
            def source_for(payload: dict) -> m.SourceRecord:
                if payload["source_url"] not in source_by_url:
                    source_by_url[payload["source_url"]] = _source(session, payload, run.id, retrieved_at)
                return source_by_url[payload["source_url"]]

            for record in normalized["standards"]:
                source = source_for(record.pop("source_record"))
                values = {k: record[k] for k in ("number", "title", "version", "status", "category", "scope")}
                values.update(source_kind="AUTHORITATIVE", publication_date=source.published_at, retrieved_at=retrieved_at)
                _, was_created = _upsert(session, m.Standard, record["id"], values)
                created += was_created; updated += not was_created
                _link(session, "standard", record["id"], source.id, f"Official metadata for {record['number']}:{record['version']}")

            guide = source_for({**fixture["sources"]["consumer_guide"], "content_hash": __import__("hashlib").sha256(json.dumps(fixture["sources"]["consumer_guide"], sort_keys=True).encode()).hexdigest()})
            _, was_created = _upsert(session, m.Document, "doc-bis-kettle-guide", {
                "title": guide.document_identifier, "document_type": "BIS_CONSUMER_GUIDE", "standard_id": "is-302-2-15-auth",
                "version": "2024-11-11", "source_url": guide.source_url, "publication_date": guide.published_at, "retrieved_at": retrieved_at,
                "source_kind": "AUTHORITATIVE", "source_authority": guide.source_authority, "verification_status": "AUTHORITATIVE",
                "document_identifier": guide.document_identifier, "content_hash": guide.content_hash, "status": "ACTIVE",
            })
            created += was_created; updated += not was_created
            guide_text = fixture["sources"]["consumer_guide"]["text"]
            _, was_created = _upsert(session, m.DocumentChunk, "chunk-bis-kettle-guide", {
                "document_id": "doc-bis-kettle-guide", "page": 1, "clause": None, "section": "Product classification",
                "heading": "Guide for safety of Electrical Appliances for Heating Liquids", "paragraph_index": 1, "text": guide_text,
                "content_hash": __import__("hashlib").sha256(guide_text.encode()).hexdigest(),
            })
            created += was_created; updated += not was_created
            _, was_created = _upsert(session, m.ProductCategory, "category-heating-liquids", {"slug": "appliances-for-heating-liquids", "name": "Appliances for Heating Liquids", "source_kind": "AUTHORITATIVE"})
            created += was_created; updated += not was_created
            _, was_created = _upsert(session, m.ProductCategory, "product-electric-kettle", {"slug": "electric-kettle", "name": "Electric Kettle", "parent_id": "category-heating-liquids", "source_kind": "AUTHORITATIVE"})
            created += was_created; updated += not was_created
            _link(session, "product_category", "product-electric-kettle", guide.id, "BIS guide identifies electric kettles as appliances for heating liquids")
            _, was_created = _upsert(session, m.ProductStandardMapping, "mapping-heating-liquids-302-2-15", {
                "product_category_id": "category-heating-liquids", "standard_id": "is-302-2-15-auth", "relationship_type": "GOVERNED_BY",
                "rationale": "The BIS guide states that IS 302-2-15 deals with appliances intended to heat liquids.", "source_record_id": guide.id,
            })
            created += was_created; updated += not was_created

            qco_record = normalized["qco"][0]
            qco_source = source_for(qco_record.pop("source_record"))
            # Preserve the superseded predecessor as a historical instrument; no absent fields are invented.
            _, predecessor_created = _upsert(session, m.QCO, "qco-household-appliances-2025", {
                "title": "Safety of Household, Commercial and Similar Electrical Appliances (Quality Control) Order, 2025",
                "status": "SUPERSEDED", "source_verified": True, "source_kind": "AUTHORITATIVE", "superseded_by_id": None,
            })
            created += predecessor_created; updated += not predecessor_created
            qco_values = {
                "title": qco_record["title"], "status": "NOTIFIED", "publication_date": _date(qco_record["publication_date"]),
                "notification_number": qco_record["notification_number"], "notification_date": _date(qco_record["notification_date"]),
                "effective_date": min(_date(x["effective_from"]) for x in qco_record["applicability"]), "source_verified": True,
                "source_kind": "AUTHORITATIVE", "source_url": qco_source.source_url, "supersedes_id": qco_record["supersedes"], "source_record_id": qco_source.id,
            }
            _, was_created = _upsert(session, m.QCO, qco_record["id"], qco_values)
            created += was_created; updated += not was_created
            session.get(m.QCO, "qco-household-appliances-2025").superseded_by_id = qco_record["id"]
            _link(session, "qco", qco_record["id"], qco_source.id, "2026 QCO notification, scope, scheme and implementation dates")
            _, was_created = _upsert(session, m.Document, "doc-qco-household-appliances-2026", {
                "title": qco_record["title"], "document_type": "OFFICIAL_GAZETTE_QCO", "standard_id": "is-302-1-2024-auth",
                "version": "S.O. 1739(E)", "source_url": qco_source.source_url, "publication_date": qco_source.published_at,
                "effective_date": _date("2026-10-01"), "retrieved_at": retrieved_at, "source_kind": "AUTHORITATIVE",
                "source_authority": qco_source.source_authority, "verification_status": "AUTHORITATIVE",
                "document_identifier": qco_source.document_identifier, "content_hash": qco_source.content_hash, "status": "NOTIFIED",
            })
            created += was_created; updated += not was_created
            qco_text = fixture["sources"]["qco_2026"]["text"]
            _, was_created = _upsert(session, m.DocumentChunk, "chunk-qco-household-appliances-2026", {
                "document_id": "doc-qco-household-appliances-2026", "page": 6, "clause": "1-2", "section": "Application, commencement and compulsory Standard Mark",
                "heading": "Safety of Household, Commercial and Similar Electrical Appliances (Quality Control) Order, 2026",
                "paragraph_index": 1, "text": qco_text, "content_hash": __import__("hashlib").sha256(qco_text.encode()).hexdigest(),
            })
            created += was_created; updated += not was_created
            for app in qco_record["applicability"]:
                app_id = f"qco-app-kettle-{app['enterprise_category'].lower()}"
                _, was_created = _upsert(session, m.QCOApplicability, app_id, {
                    "qco_id": qco_record["id"], "enterprise_category": app["enterprise_category"],
                    "covered_product_category": "appliances-for-heating-liquids", "standard_reference": "IS 302 (Part 1):2024 / IEC 60335-1:2020",
                    "effective_from": _date(app["effective_from"]), "source_record_id": qco_source.id,
                })
                created += was_created; updated += not was_created
            for standard_id in ("is-302-1-2024-auth", "is-302-2-15-auth"):
                _, was_created = _upsert(session, m.StandardQCO, f"sqco-{standard_id[-20:]}", {"standard_id": standard_id, "qco_id": qco_record["id"]})
                created += was_created; updated += not was_created
            _, was_created = _upsert(session, m.StandardRelationship, "rel-302-2-15-to-part1-2024", {
                "source_standard_id": "is-302-2-15-auth", "target_standard_id": "is-302-1-2024-auth", "relationship_type": "USES_GENERAL_SAFETY_FRAMEWORK",
                "rationale": "The QCO applies Part 1 to Appliances for Heating Liquids; LIMS scope lists Part 1 test clauses alongside Part 2/Sec 15.", "source_record_id": qco_source.id,
            })
            created += was_created; updated += not was_created

            scheme = normalized["compulsory-certification"][0]
            scheme_source = source_for(scheme.pop("source_record"))
            _, was_created = _upsert(session, m.CertificationScheme, scheme["id"], {
                "standard_id": scheme["standard_id"], "qco_id": scheme["qco_id"], "name": scheme["name"],
                "description": "Standard Mark licence under Scheme I of Schedule II of the BIS Conformity Assessment Regulations, 2018.",
                "source_kind": "AUTHORITATIVE", "source_record_id": scheme_source.id,
            })
            created += was_created; updated += not was_created

            manual = normalized["product-manuals"][0]
            manual_source = source_for(manual.pop("source_record"))
            document_id = "doc-pm-is-302-2-15-2024"
            _, was_created = _upsert(session, m.Document, document_id, {
                "title": manual["manual_identifier"], "document_type": "BIS_PRODUCT_MANUAL", "standard_id": manual["standard_id"],
                "version": "February 2024", "source_url": manual_source.source_url, "publication_date": manual_source.published_at,
                "retrieved_at": retrieved_at, "source_kind": "AUTHORITATIVE", "source_authority": manual_source.source_authority,
                "verification_status": "AUTHORITATIVE", "document_identifier": manual["manual_identifier"], "content_hash": manual_source.content_hash, "status": "ACTIVE",
            })
            created += was_created; updated += not was_created
            _, was_created = _upsert(session, m.ProductManual, manual["id"], {
                "standard_id": manual["standard_id"], "document_id": document_id, "source_kind": "AUTHORITATIVE",
                "manual_identifier": manual["manual_identifier"], "status": manual["status"], "source_record_id": manual_source.id,
            })
            created += was_created; updated += not was_created
            for index, chunk in enumerate(ClauseAwareParser().parse_pages(manual["pages"]), start=1):
                _, was_created = _upsert(session, m.DocumentChunk, f"chunk-kettle-manual-{index}", {
                    "document_id": document_id, "page": chunk.page, "clause": chunk.clause, "section": chunk.heading,
                    "heading": chunk.heading, "subclause": chunk.subclause, "table_label": chunk.table_label,
                    "paragraph_index": chunk.paragraph_index, "text": chunk.text, "content_hash": chunk.content_hash,
                })
                created += was_created; updated += not was_created

            lab_source_first = None
            for record in normalized["labs"]:
                lab_source = source_for(record.pop("source_record")); lab_source_first = lab_source_first or lab_source
                lab_values = {k: record.get(k) for k in ("name", "address", "city", "state")}
                lab_values["source_kind"] = "AUTHORITATIVE"
                _, was_created = _upsert(session, m.Laboratory, record["id"], lab_values)
                created += was_created; updated += not was_created
                _, was_created = _upsert(session, m.LaboratoryRecognition, f"rec-{record['id']}-kettle", {
                    "laboratory_id": record["id"], "standard_id": "is-302-2-15-auth", "valid_until": _date(record["valid_until"]),
                    "capabilities": ["Testing to listed IS 302 (Part 2/Sec 15):2009 scope"], "source_kind": "AUTHORITATIVE",
                    "scope_identifier": record["scope_identifier"], "scope": record["scope"], "test_clauses": record["test_clauses"],
                    "status": record["status"], "source_url": lab_source.source_url, "retrieved_at": retrieved_at,
                    "verification_status": "AUTHORITATIVE", "source_record_id": lab_source.id,
                })
                created += was_created; updated += not was_created
                _link(session, "laboratory_recognition", f"rec-{record['id']}-kettle", lab_source.id, "BIS LIMS recognition scope and validity")

            test_source = lab_source_first
            for clause, name in (("7", "Marking and instructions"), ("10", "Power input and current"), ("11", "Heating"), ("13", "Leakage current and electric strength at operating temperature"), ("15", "Moisture resistance"), ("19", "Abnormal operation"), ("21", "Mechanical strength"), ("30", "Resistance to heat and fire")):
                _, was_created = _upsert(session, m.Test, f"test-kettle-{clause}", {"standard_id": "is-302-2-15-auth", "name": name, "clause": clause, "source_kind": "AUTHORITATIVE", "source_record_id": test_source.id})
                created += was_created; updated += not was_created

            if dry_run:
                raise _DryRunRollback()
        run.status = "SUCCESS"
    except _DryRunRollback:
        run.status = "SUCCESS"
        created = updated = 0
    except Exception as exc:
        session.rollback()
        run = session.get(m.IngestionRun, run.id)
        run.status = "FAILED"
        run.records_rejected = max(run.records_fetched, 1)
        run.errors = [str(exc)]
        run.finished_at = datetime.now(timezone.utc)
        session.commit()
        raise
    run.records_created = created
    run.records_updated = updated
    run.records_rejected = rejected
    run.finished_at = datetime.now(timezone.utc)
    session.commit()
    return {"run_id": run.id, "status": run.status, "records_fetched": run.records_fetched, "records_created": created, "records_updated": updated, "dry_run": dry_run}


class _DryRunRollback(Exception):
    pass


def embed_document_chunks(session: Session, provider, *, authoritative_only: bool = True) -> dict:
    statement = select(m.DocumentChunk).join(m.Document)
    if authoritative_only:
        statement = statement.where(m.Document.source_kind == "AUTHORITATIVE")
    chunks = list(session.scalars(statement.order_by(m.DocumentChunk.id)))
    vectors = provider.embed([chunk.text for chunk in chunks])
    if chunks and len(vectors) != len(chunks):
        raise RuntimeError("Embedding provider returned an unexpected vector count")
    for chunk, vector in zip(chunks, vectors):
        if len(vector) != 384:
            raise RuntimeError("Embedding vector dimension must be 384")
        chunk.embedding = vector
    session.commit()
    return {"chunks_embedded": len(vectors), "dimensions": 384}
