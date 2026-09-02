"""Relational PostgreSQL domain model used by repositories and migrations."""
from datetime import date, datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PortableVector(TypeDecorator):
    """Use pgvector on PostgreSQL and JSON in lightweight integration tests."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Vector(384))
        return dialect.type_descriptor(JSON())


class Base(DeclarativeBase):
    pass


class IdMixin:
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class User(IdMixin, Base):
    __tablename__ = "users"
    email: Mapped[str | None] = mapped_column(String(320), unique=True, index=True)
    preferred_language: Mapped[str] = mapped_column(String(16), default="en")


class Product(IdMixin, Base):
    __tablename__ = "products"
    name: Mapped[str] = mapped_column(String(300), index=True)
    category: Mapped[str | None] = mapped_column(String(200), index=True)
    source_kind: Mapped[str] = mapped_column(String(24), default="DEMO", index=True)


class ProductProfile(IdMixin, Base):
    __tablename__ = "product_profiles"
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(64))
    input_description: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(16), default="en")
    attributes: Mapped[list] = mapped_column(JSON, default=list)
    missing_attributes: Mapped[list] = mapped_column(JSON, default=list)
    structured_attributes: Mapped[dict] = mapped_column(JSON, default=dict)
    product: Mapped["Product"] = relationship()


class Conversation(IdMixin, Base):
    __tablename__ = "conversations"
    detected_language: Mapped[str] = mapped_column(String(16), default="en")
    current_intent: Mapped[str] = mapped_column(String(48), default="UNKNOWN", index=True)
    structured_state: Mapped[dict] = mapped_column(JSON, default=dict)
    unresolved_attributes: Mapped[list] = mapped_column(JSON, default=list)
    active_compliance_profile_id: Mapped[str | None] = mapped_column(String(64), index=True)
    relevant_standard_id: Mapped[str | None] = mapped_column(String(64), index=True)
    evidence_references: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class ConversationMessage(IdMixin, Base):
    __tablename__ = "conversation_messages"
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(16), index=True)
    content: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(16), default="en")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class AIUsageEvent(IdMixin, Base):
    __tablename__ = "ai_usage_events"
    provider: Mapped[str] = mapped_column(String(32), index=True)
    model: Mapped[str | None] = mapped_column(String(120), index=True)
    operation: Mapped[str] = mapped_column(String(48), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    request_id: Mapped[str | None] = mapped_column(String(64), index=True)
    conversation_id: Mapped[str | None] = mapped_column(String(64), index=True)
    validation_result: Mapped[str | None] = mapped_column(String(32), index=True)
    validation_reason: Mapped[str | None] = mapped_column(String(240))


class SourceChangeEvent(IdMixin, Base):
    __tablename__ = "source_change_events"
    source_url: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(80), index=True)
    previous_hash: Mapped[str] = mapped_column(String(64))
    new_hash: Mapped[str] = mapped_column(String(64))
    ingestion_run_id: Mapped[str | None] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="REVIEW_REQUIRED", index=True)


class Standard(IdMixin, Base):
    __tablename__ = "standards"
    __table_args__ = (UniqueConstraint("number", "version", "source_kind", name="uq_standard_number_version_source"),)
    number: Mapped[str] = mapped_column(String(120), index=True)
    title: Mapped[str] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), index=True)
    category: Mapped[str] = mapped_column(String(120), index=True)
    scope: Mapped[str] = mapped_column(Text)
    publication_date: Mapped[date | None] = mapped_column(Date)
    effective_date: Mapped[date | None] = mapped_column(Date, index=True)
    superseded_by_id: Mapped[str | None] = mapped_column(ForeignKey("standards.id"))
    source_kind: Mapped[str] = mapped_column(String(24), default="DEMO", index=True)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class IngestionRun(IdMixin, Base):
    __tablename__ = "ingestion_runs"
    adapter: Mapped[str] = mapped_column(String(120), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(24), default="RUNNING", index=True)
    records_fetched: Mapped[int] = mapped_column(Integer, default=0)
    records_created: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_rejected: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[list] = mapped_column(JSON, default=list)


class SourceRecord(IdMixin, Base):
    __tablename__ = "source_records"
    __table_args__ = (UniqueConstraint("source_url", "content_hash", name="uq_source_url_content_hash"),)
    source_url: Mapped[str] = mapped_column(Text)
    source_authority: Mapped[str] = mapped_column(String(160))
    source_type: Mapped[str] = mapped_column(String(80), index=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[date | None] = mapped_column(Date)
    effective_from: Mapped[date | None] = mapped_column(Date)
    effective_until: Mapped[date | None] = mapped_column(Date)
    document_identifier: Mapped[str | None] = mapped_column(String(240), index=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    ingestion_run_id: Mapped[str | None] = mapped_column(ForeignKey("ingestion_runs.id"), index=True)
    verification_status: Mapped[str] = mapped_column(String(32), index=True)
    page: Mapped[int | None] = mapped_column(Integer)
    clause: Mapped[str | None] = mapped_column(String(64))
    section: Mapped[str | None] = mapped_column(Text)
    table_label: Mapped[str | None] = mapped_column(String(160))
    row_reference: Mapped[str | None] = mapped_column(String(160))
    official_notification_number: Mapped[str | None] = mapped_column(String(120), index=True)
    gazette_reference: Mapped[str | None] = mapped_column(String(160))
    standard_number: Mapped[str | None] = mapped_column(String(120), index=True)
    standard_year: Mapped[int | None] = mapped_column(Integer)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class ProvenanceLink(IdMixin, Base):
    __tablename__ = "provenance_links"
    __table_args__ = (UniqueConstraint("record_type", "record_id", "source_record_id", name="uq_provenance_link"),)
    record_type: Mapped[str] = mapped_column(String(80), index=True)
    record_id: Mapped[str] = mapped_column(String(64), index=True)
    source_record_id: Mapped[str] = mapped_column(ForeignKey("source_records.id", ondelete="CASCADE"), index=True)
    claim: Mapped[str | None] = mapped_column(Text)
    source_record: Mapped["SourceRecord"] = relationship()


class ProductCategory(IdMixin, Base):
    __tablename__ = "product_categories"
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(240))
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("product_categories.id"))
    source_kind: Mapped[str] = mapped_column(String(24), default="DEMO", index=True)


class ProductStandardMapping(IdMixin, Base):
    __tablename__ = "product_standard_mappings"
    __table_args__ = (UniqueConstraint("product_category_id", "standard_id", "relationship_type", name="uq_product_standard_mapping"),)
    product_category_id: Mapped[str] = mapped_column(ForeignKey("product_categories.id", ondelete="CASCADE"), index=True)
    standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id", ondelete="CASCADE"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(64))
    rationale: Mapped[str] = mapped_column(Text)
    source_record_id: Mapped[str] = mapped_column(ForeignKey("source_records.id"))


class StandardRelationship(IdMixin, Base):
    __tablename__ = "standard_relationships"
    __table_args__ = (
        UniqueConstraint("source_standard_id", "target_standard_id", "relationship_type", name="uq_standard_relationship"),
        Index("ix_standard_relationship_source_type", "source_standard_id", "relationship_type"),
    )
    source_standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id", ondelete="CASCADE"))
    target_standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id", ondelete="CASCADE"))
    relationship_type: Mapped[str] = mapped_column(String(40))
    rationale: Mapped[str | None] = mapped_column(Text)
    source_record_id: Mapped[str | None] = mapped_column(ForeignKey("source_records.id"))
    source: Mapped["Standard"] = relationship(foreign_keys=[source_standard_id])
    target: Mapped["Standard"] = relationship(foreign_keys=[target_standard_id])


class Document(IdMixin, Base):
    __tablename__ = "documents"
    title: Mapped[str] = mapped_column(Text)
    document_type: Mapped[str] = mapped_column(String(80), index=True)
    standard_id: Mapped[str | None] = mapped_column(ForeignKey("standards.id"), index=True)
    version: Mapped[str | None] = mapped_column(String(64))
    source_url: Mapped[str | None] = mapped_column(Text)
    publication_date: Mapped[date | None] = mapped_column(Date)
    effective_date: Mapped[date | None] = mapped_column(Date)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_kind: Mapped[str] = mapped_column(String(24), default="DEMO", index=True)
    source_authority: Mapped[str | None] = mapped_column(String(160))
    verification_status: Mapped[str] = mapped_column(String(32), default="UNVERIFIED", index=True)
    document_identifier: Mapped[str | None] = mapped_column(String(240), index=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    effective_until: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="UNKNOWN", index=True)
    standard: Mapped["Standard | None"] = relationship()


class DocumentChunk(IdMixin, Base):
    __tablename__ = "document_chunks"
    __table_args__ = (Index("ix_document_chunk_document_clause", "document_id", "clause"),)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    page: Mapped[int | None] = mapped_column(Integer)
    clause: Mapped[str | None] = mapped_column(String(64))
    section: Mapped[str | None] = mapped_column(Text)
    heading: Mapped[str | None] = mapped_column(Text)
    subclause: Mapped[str | None] = mapped_column(String(64))
    table_label: Mapped[str | None] = mapped_column(String(160))
    paragraph_index: Mapped[int | None] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    embedding: Mapped[list | None] = mapped_column(PortableVector())
    document: Mapped["Document"] = relationship()


class QCO(IdMixin, Base):
    __tablename__ = "qcos"
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), index=True)
    publication_date: Mapped[date | None] = mapped_column(Date)
    effective_date: Mapped[date | None] = mapped_column(Date, index=True)
    source_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    source_kind: Mapped[str] = mapped_column(String(24), default="DEMO", index=True)
    source_url: Mapped[str | None] = mapped_column(Text)
    notification_number: Mapped[str | None] = mapped_column(String(120), index=True)
    notification_date: Mapped[date | None] = mapped_column(Date)
    effective_until: Mapped[date | None] = mapped_column(Date)
    supersedes_id: Mapped[str | None] = mapped_column(ForeignKey("qcos.id"))
    superseded_by_id: Mapped[str | None] = mapped_column(ForeignKey("qcos.id"))
    source_record_id: Mapped[str | None] = mapped_column(ForeignKey("source_records.id"))


class QCOApplicability(IdMixin, Base):
    __tablename__ = "qco_applicability"
    __table_args__ = (UniqueConstraint("qco_id", "enterprise_category", "covered_product_category", name="uq_qco_applicability"),)
    qco_id: Mapped[str] = mapped_column(ForeignKey("qcos.id", ondelete="CASCADE"), index=True)
    enterprise_category: Mapped[str] = mapped_column(String(32), index=True)
    covered_product_category: Mapped[str] = mapped_column(String(240), index=True)
    standard_reference: Mapped[str] = mapped_column(String(160))
    effective_from: Mapped[date] = mapped_column(Date, index=True)
    effective_until: Mapped[date | None] = mapped_column(Date)
    source_record_id: Mapped[str] = mapped_column(ForeignKey("source_records.id"))


class CertificationScheme(IdMixin, Base):
    __tablename__ = "certification_schemes"
    standard_id: Mapped[str | None] = mapped_column(ForeignKey("standards.id"), index=True)
    name: Mapped[str] = mapped_column(String(240))
    description: Mapped[str | None] = mapped_column(Text)
    source_kind: Mapped[str] = mapped_column(String(24), default="DEMO")
    qco_id: Mapped[str | None] = mapped_column(ForeignKey("qcos.id"), index=True)
    source_record_id: Mapped[str | None] = mapped_column(ForeignKey("source_records.id"))


class Test(IdMixin, Base):
    __tablename__ = "tests"
    standard_id: Mapped[str | None] = mapped_column(ForeignKey("standards.id"), index=True)
    name: Mapped[str] = mapped_column(String(240))
    clause: Mapped[str | None] = mapped_column(String(64))
    source_kind: Mapped[str] = mapped_column(String(24), default="DEMO")
    source_record_id: Mapped[str | None] = mapped_column(ForeignKey("source_records.id"))


class Laboratory(IdMixin, Base):
    __tablename__ = "laboratories"
    name: Mapped[str] = mapped_column(String(300), index=True)
    city: Mapped[str | None] = mapped_column(String(120), index=True)
    state: Mapped[str | None] = mapped_column(String(120), index=True)
    address: Mapped[str | None] = mapped_column(Text)
    source_kind: Mapped[str] = mapped_column(String(24), default="DEMO", index=True)


class LaboratoryRecognition(IdMixin, Base):
    __tablename__ = "laboratory_recognitions"
    __table_args__ = (UniqueConstraint("laboratory_id", "standard_id", name="uq_lab_standard_recognition"),)
    laboratory_id: Mapped[str] = mapped_column(ForeignKey("laboratories.id", ondelete="CASCADE"), index=True)
    standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id", ondelete="CASCADE"), index=True)
    valid_until: Mapped[date | None] = mapped_column(Date)
    valid_from: Mapped[date | None] = mapped_column(Date)
    capabilities: Mapped[list] = mapped_column(JSON, default=list)
    source_kind: Mapped[str] = mapped_column(String(24), default="DEMO")
    scope_identifier: Mapped[str | None] = mapped_column(String(120))
    scope: Mapped[str | None] = mapped_column(Text)
    test_clauses: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="UNKNOWN", index=True)
    source_url: Mapped[str | None] = mapped_column(Text)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_status: Mapped[str] = mapped_column(String(32), default="UNVERIFIED", index=True)
    source_record_id: Mapped[str | None] = mapped_column(ForeignKey("source_records.id"))
    laboratory: Mapped["Laboratory"] = relationship()
    standard: Mapped["Standard"] = relationship()


class ProductManual(IdMixin, Base):
    __tablename__ = "product_manuals"
    standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id", ondelete="CASCADE"), index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), unique=True)
    source_kind: Mapped[str] = mapped_column(String(24), default="DEMO")
    manual_identifier: Mapped[str | None] = mapped_column(String(240), index=True)
    status: Mapped[str] = mapped_column(String(32), default="UNKNOWN")
    source_record_id: Mapped[str | None] = mapped_column(ForeignKey("source_records.id"))


class ComplianceRule(IdMixin, Base):
    __tablename__ = "compliance_rules"
    standard_id: Mapped[str | None] = mapped_column(ForeignKey("standards.id"), index=True)
    name: Mapped[str] = mapped_column(String(240))
    priority: Mapped[int] = mapped_column(Integer, default=100)
    conditions: Mapped[dict] = mapped_column(JSON)
    outcome: Mapped[dict] = mapped_column(JSON)
    source_kind: Mapped[str] = mapped_column(String(24), default="DEMO")


class ComplianceProfile(IdMixin, Base):
    __tablename__ = "compliance_profiles"
    product_profile_id: Mapped[str] = mapped_column(ForeignKey("product_profiles.id", ondelete="CASCADE"), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    mandatory_status: Mapped[str] = mapped_column(String(40), index=True)
    qco_id: Mapped[str | None] = mapped_column(ForeignKey("qcos.id"))
    certification_scheme_id: Mapped[str | None] = mapped_column(ForeignKey("certification_schemes.id"))
    tests: Mapped[list] = mapped_column(JSON, default=list)
    required_documents: Mapped[list] = mapped_column(JSON, default=list)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    as_of_date: Mapped[date | None] = mapped_column(Date, index=True)
    data_mode: Mapped[str] = mapped_column(String(24), default="DEMO", index=True)
    explanation_tree: Mapped[dict] = mapped_column(JSON, default=dict)
    product_profile: Mapped["ProductProfile"] = relationship()
    qco: Mapped["QCO | None"] = relationship()
    certification_scheme: Mapped["CertificationScheme | None"] = relationship()


class ComplianceJourney(IdMixin, Base):
    __tablename__ = "compliance_journeys"
    compliance_profile_id: Mapped[str] = mapped_column(ForeignKey("compliance_profiles.id", ondelete="CASCADE"), unique=True)
    steps: Mapped[list] = mapped_column(JSON, default=list)


class Citation(IdMixin, Base):
    __tablename__ = "citations"
    compliance_profile_id: Mapped[str | None] = mapped_column(ForeignKey("compliance_profiles.id", ondelete="CASCADE"), index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    chunk_id: Mapped[str | None] = mapped_column(ForeignKey("document_chunks.id"))
    claim: Mapped[str] = mapped_column(Text)
    source_kind: Mapped[str] = mapped_column(String(24), default="DEMO")
    validation_status: Mapped[str] = mapped_column(String(32), default="PENDING")
    validation_error: Mapped[str | None] = mapped_column(Text)
    document: Mapped["Document"] = relationship()
    chunk: Mapped["DocumentChunk | None"] = relationship()


class ComplianceProfileStandard(IdMixin, Base):
    __tablename__ = "compliance_profile_standards"
    __table_args__ = (UniqueConstraint("compliance_profile_id", "standard_id", name="uq_profile_standard"),)
    compliance_profile_id: Mapped[str] = mapped_column(ForeignKey("compliance_profiles.id", ondelete="CASCADE"), index=True)
    standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id"), index=True)


class StandardQCO(IdMixin, Base):
    __tablename__ = "standard_qcos"
    __table_args__ = (UniqueConstraint("standard_id", "qco_id", name="uq_standard_qco"),)
    standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id", ondelete="CASCADE"), index=True)
    qco_id: Mapped[str] = mapped_column(ForeignKey("qcos.id", ondelete="CASCADE"), index=True)
