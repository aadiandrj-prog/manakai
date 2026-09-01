"""Relational domain model for PostgreSQL.

The demo API reads in-memory fixtures; these SQLAlchemy models define the durable
schema boundary used when PostgreSQL is enabled.
"""
from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class IdMixin:
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class User(IdMixin, Base):
    __tablename__ = "users"
    email: Mapped[str | None] = mapped_column(String(320), unique=True)
    preferred_language: Mapped[str] = mapped_column(String(16), default="en")


class Product(IdMixin, Base):
    __tablename__ = "products"
    name: Mapped[str] = mapped_column(String(300))
    category: Mapped[str | None] = mapped_column(String(200))


class ProductProfile(IdMixin, Base):
    __tablename__ = "product_profiles"
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    role: Mapped[str] = mapped_column(String(64))
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict)
    missing_attributes: Mapped[list] = mapped_column(JSONB, default=list)


class Standard(IdMixin, Base):
    __tablename__ = "standards"
    number: Mapped[str] = mapped_column(String(120), index=True)
    title: Mapped[str] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), index=True)
    publication_date: Mapped[date | None] = mapped_column(Date)
    effective_date: Mapped[date | None] = mapped_column(Date)
    superseded_by_id: Mapped[str | None] = mapped_column(ForeignKey("standards.id"))


class StandardRelationship(IdMixin, Base):
    __tablename__ = "standard_relationships"
    source_standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id"))
    target_standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id"))
    relationship_type: Mapped[str] = mapped_column(String(40))


class Document(IdMixin, Base):
    __tablename__ = "documents"
    title: Mapped[str] = mapped_column(Text)
    document_type: Mapped[str] = mapped_column(String(80))
    standard_id: Mapped[str | None] = mapped_column(ForeignKey("standards.id"))
    source_url: Mapped[str | None] = mapped_column(Text)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime)


class DocumentChunk(IdMixin, Base):
    __tablename__ = "document_chunks"
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"))
    page: Mapped[int | None]
    clause: Mapped[str | None] = mapped_column(String(64))
    section: Mapped[str | None] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list | None] = mapped_column(JSONB)  # replace with pgvector Vector after extension migration


class QCO(IdMixin, Base):
    __tablename__ = "qcos"
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32))
    effective_date: Mapped[date | None] = mapped_column(Date)
    source_verified: Mapped[bool] = mapped_column(Boolean, default=False)


class CertificationScheme(IdMixin, Base):
    __tablename__ = "certification_schemes"
    name: Mapped[str] = mapped_column(String(240))
    description: Mapped[str | None] = mapped_column(Text)


class Test(IdMixin, Base):
    __tablename__ = "tests"
    name: Mapped[str] = mapped_column(String(240))
    standard_id: Mapped[str | None] = mapped_column(ForeignKey("standards.id"))
    clause: Mapped[str | None] = mapped_column(String(64))


class Laboratory(IdMixin, Base):
    __tablename__ = "laboratories"
    name: Mapped[str] = mapped_column(String(300))
    city: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(120))
    address: Mapped[str | None] = mapped_column(Text)


class LaboratoryRecognition(IdMixin, Base):
    __tablename__ = "laboratory_recognitions"
    laboratory_id: Mapped[str] = mapped_column(ForeignKey("laboratories.id"))
    standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id"))
    valid_until: Mapped[date | None] = mapped_column(Date)
    scope: Mapped[dict] = mapped_column(JSONB, default=dict)


class ProductManual(IdMixin, Base):
    __tablename__ = "product_manuals"
    standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id"))
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"))


class ComplianceRule(IdMixin, Base):
    __tablename__ = "compliance_rules"
    name: Mapped[str] = mapped_column(String(240))
    priority: Mapped[int] = mapped_column(default=100)
    conditions: Mapped[dict] = mapped_column(JSONB)
    outcome: Mapped[dict] = mapped_column(JSONB)


class ComplianceProfile(IdMixin, Base):
    __tablename__ = "compliance_profiles"
    product_profile_id: Mapped[str] = mapped_column(ForeignKey("product_profiles.id"))
    confidence: Mapped[float] = mapped_column(Float)
    mandatory_status: Mapped[str] = mapped_column(String(40))
    warnings: Mapped[list] = mapped_column(JSONB, default=list)


class ComplianceJourney(IdMixin, Base):
    __tablename__ = "compliance_journeys"
    compliance_profile_id: Mapped[str] = mapped_column(ForeignKey("compliance_profiles.id"))
    steps: Mapped[list] = mapped_column(JSONB, default=list)


class Citation(IdMixin, Base):
    __tablename__ = "citations"
    compliance_profile_id: Mapped[str | None] = mapped_column(ForeignKey("compliance_profiles.id"))
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"))
    chunk_id: Mapped[str | None] = mapped_column(ForeignKey("document_chunks.id"))
    claim: Mapped[str] = mapped_column(Text)


class ComplianceProfileStandard(IdMixin, Base):
    __tablename__ = "compliance_profile_standards"
    compliance_profile_id: Mapped[str] = mapped_column(ForeignKey("compliance_profiles.id"))
    standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id"))


class StandardQCO(IdMixin, Base):
    __tablename__ = "standard_qcos"
    standard_id: Mapped[str] = mapped_column(ForeignKey("standards.id"))
    qco_id: Mapped[str] = mapped_column(ForeignKey("qcos.id"))
