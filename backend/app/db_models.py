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
    source_kind: Mapped[str] = mapped_column(String(24), default="demo", index=True)


class ProductProfile(IdMixin, Base):
    __tablename__ = "product_profiles"
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(64))
    input_description: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(16), default="en")
    attributes: Mapped[list] = mapped_column(JSON, default=list)
    missing_attributes: Mapped[list] = mapped_column(JSON, default=list)
    product: Mapped["Product"] = relationship()


class Standard(IdMixin, Base):
    __tablename__ = "standards"
    __table_args__ = (UniqueConstraint("number", "version", name="uq_standard_number_version"),)
    number: Mapped[str] = mapped_column(String(120), index=True)
    title: Mapped[str] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), index=True)
    category: Mapped[str] = mapped_column(String(120), index=True)
    scope: Mapped[str] = mapped_column(Text)
    publication_date: Mapped[date | None] = mapped_column(Date)
    effective_date: Mapped[date | None] = mapped_column(Date, index=True)
    superseded_by_id: Mapped[str | None] = mapped_column(ForeignKey("standards.id"))
    source_kind: Mapped[str] = mapped_column(String(24), default="demo", index=True)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class StandardRelationship(IdMixin, Base):
    __tablename__ = "standard_relationships"
    __table_args__ = (
        UniqueConstraint("source_standard_id", "target_standard_id", "relationship_type", name="uq_standard_relationship"),
        Index("ix_standard_relationship_source_type", "source_standard_id", "relationship_type"),
    )
    source_standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id", ondelete="CASCADE"))
    target_standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id", ondelete="CASCADE"))
    relationship_type: Mapped[str] = mapped_column(String(40))
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
    source_kind: Mapped[str] = mapped_column(String(24), default="demo", index=True)
    standard: Mapped["Standard | None"] = relationship()


class DocumentChunk(IdMixin, Base):
    __tablename__ = "document_chunks"
    __table_args__ = (Index("ix_document_chunk_document_clause", "document_id", "clause"),)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    page: Mapped[int | None] = mapped_column(Integer)
    clause: Mapped[str | None] = mapped_column(String(64))
    section: Mapped[str | None] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list | None] = mapped_column(PortableVector())
    document: Mapped["Document"] = relationship()


class QCO(IdMixin, Base):
    __tablename__ = "qcos"
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), index=True)
    publication_date: Mapped[date | None] = mapped_column(Date)
    effective_date: Mapped[date | None] = mapped_column(Date, index=True)
    source_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    source_kind: Mapped[str] = mapped_column(String(24), default="demo", index=True)
    source_url: Mapped[str | None] = mapped_column(Text)


class CertificationScheme(IdMixin, Base):
    __tablename__ = "certification_schemes"
    standard_id: Mapped[str | None] = mapped_column(ForeignKey("standards.id"), index=True)
    name: Mapped[str] = mapped_column(String(240))
    description: Mapped[str | None] = mapped_column(Text)
    source_kind: Mapped[str] = mapped_column(String(24), default="demo")


class Test(IdMixin, Base):
    __tablename__ = "tests"
    standard_id: Mapped[str | None] = mapped_column(ForeignKey("standards.id"), index=True)
    name: Mapped[str] = mapped_column(String(240))
    clause: Mapped[str | None] = mapped_column(String(64))
    source_kind: Mapped[str] = mapped_column(String(24), default="demo")


class Laboratory(IdMixin, Base):
    __tablename__ = "laboratories"
    name: Mapped[str] = mapped_column(String(300), index=True)
    city: Mapped[str | None] = mapped_column(String(120), index=True)
    state: Mapped[str | None] = mapped_column(String(120), index=True)
    address: Mapped[str | None] = mapped_column(Text)
    source_kind: Mapped[str] = mapped_column(String(24), default="demo", index=True)


class LaboratoryRecognition(IdMixin, Base):
    __tablename__ = "laboratory_recognitions"
    __table_args__ = (UniqueConstraint("laboratory_id", "standard_id", name="uq_lab_standard_recognition"),)
    laboratory_id: Mapped[str] = mapped_column(ForeignKey("laboratories.id", ondelete="CASCADE"), index=True)
    standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id", ondelete="CASCADE"), index=True)
    valid_until: Mapped[date | None] = mapped_column(Date)
    capabilities: Mapped[list] = mapped_column(JSON, default=list)
    source_kind: Mapped[str] = mapped_column(String(24), default="demo")
    laboratory: Mapped["Laboratory"] = relationship()
    standard: Mapped["Standard"] = relationship()


class ProductManual(IdMixin, Base):
    __tablename__ = "product_manuals"
    standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id", ondelete="CASCADE"), index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), unique=True)
    source_kind: Mapped[str] = mapped_column(String(24), default="demo")


class ComplianceRule(IdMixin, Base):
    __tablename__ = "compliance_rules"
    standard_id: Mapped[str | None] = mapped_column(ForeignKey("standards.id"), index=True)
    name: Mapped[str] = mapped_column(String(240))
    priority: Mapped[int] = mapped_column(Integer, default=100)
    conditions: Mapped[dict] = mapped_column(JSON)
    outcome: Mapped[dict] = mapped_column(JSON)
    source_kind: Mapped[str] = mapped_column(String(24), default="demo")


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
    source_kind: Mapped[str] = mapped_column(String(24), default="demo")
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
