"""authoritative BIS vertical provenance and temporal model

Revision ID: 4b2f2a8d1c71
Revises: 9072150daaa0
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4b2f2a8d1c71"
down_revision: Union[str, None] = "9072150daaa0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ingestion_runs",
        sa.Column("adapter", sa.String(120), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("records_fetched", sa.Integer(), nullable=False),
        sa.Column("records_created", sa.Integer(), nullable=False),
        sa.Column("records_updated", sa.Integer(), nullable=False),
        sa.Column("records_rejected", sa.Integer(), nullable=False),
        sa.Column("errors", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ingestion_runs_adapter", "ingestion_runs", ["adapter"])
    op.create_index("ix_ingestion_runs_status", "ingestion_runs", ["status"])
    op.create_table(
        "source_records",
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_authority", sa.String(160), nullable=False),
        sa.Column("source_type", sa.String(80), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.Date()),
        sa.Column("effective_from", sa.Date()),
        sa.Column("effective_until", sa.Date()),
        sa.Column("document_identifier", sa.String(240)),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("ingestion_run_id", sa.String(64), sa.ForeignKey("ingestion_runs.id")),
        sa.Column("verification_status", sa.String(32), nullable=False),
        sa.Column("page", sa.Integer()),
        sa.Column("clause", sa.String(64)),
        sa.Column("section", sa.Text()),
        sa.Column("table_label", sa.String(160)),
        sa.Column("row_reference", sa.String(160)),
        sa.Column("official_notification_number", sa.String(120)),
        sa.Column("gazette_reference", sa.String(160)),
        sa.Column("standard_number", sa.String(120)),
        sa.Column("standard_year", sa.Integer()),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_url", "content_hash", name="uq_source_url_content_hash"),
    )
    for column in ("source_type", "document_identifier", "content_hash", "ingestion_run_id", "verification_status", "official_notification_number", "standard_number"):
        op.create_index(f"ix_source_records_{column}", "source_records", [column])
    op.create_table(
        "provenance_links",
        sa.Column("record_type", sa.String(80), nullable=False),
        sa.Column("record_id", sa.String(64), nullable=False),
        sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("claim", sa.Text()),
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("record_type", "record_id", "source_record_id", name="uq_provenance_link"),
    )
    for column in ("record_type", "record_id", "source_record_id"):
        op.create_index(f"ix_provenance_links_{column}", "provenance_links", [column])

    op.add_column("product_profiles", sa.Column("structured_attributes", sa.JSON(), nullable=False, server_default="{}"))
    op.add_column("standard_relationships", sa.Column("rationale", sa.Text()))
    op.add_column("standard_relationships", sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id")))

    op.create_table(
        "product_categories",
        sa.Column("slug", sa.String(120), nullable=False, unique=True),
        sa.Column("name", sa.String(240), nullable=False),
        sa.Column("parent_id", sa.String(64), sa.ForeignKey("product_categories.id")),
        sa.Column("source_kind", sa.String(24), nullable=False),
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_product_categories_slug", "product_categories", ["slug"])
    op.create_index("ix_product_categories_source_kind", "product_categories", ["source_kind"])
    op.create_table(
        "product_standard_mappings",
        sa.Column("product_category_id", sa.String(64), sa.ForeignKey("product_categories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("standard_id", sa.String(64), sa.ForeignKey("standards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relationship_type", sa.String(64), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id"), nullable=False),
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("product_category_id", "standard_id", "relationship_type", name="uq_product_standard_mapping"),
    )
    op.create_index("ix_product_standard_mappings_product_category_id", "product_standard_mappings", ["product_category_id"])
    op.create_index("ix_product_standard_mappings_standard_id", "product_standard_mappings", ["standard_id"])

    document_columns = [
        sa.Column("source_authority", sa.String(160)),
        sa.Column("verification_status", sa.String(32), nullable=False, server_default="UNVERIFIED"),
        sa.Column("document_identifier", sa.String(240)),
        sa.Column("content_hash", sa.String(64)),
        sa.Column("effective_until", sa.Date()),
        sa.Column("status", sa.String(32), nullable=False, server_default="UNKNOWN"),
    ]
    for column in document_columns:
        op.add_column("documents", column)
    for column in ("verification_status", "document_identifier", "content_hash", "status"):
        op.create_index(f"ix_documents_{column}", "documents", [column])

    for column in (
        sa.Column("heading", sa.Text()),
        sa.Column("subclause", sa.String(64)),
        sa.Column("table_label", sa.String(160)),
        sa.Column("paragraph_index", sa.Integer()),
        sa.Column("content_hash", sa.String(64)),
    ):
        op.add_column("document_chunks", column)
    op.create_index("ix_document_chunks_content_hash", "document_chunks", ["content_hash"])
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE INDEX ix_document_chunks_fts ON document_chunks USING gin (to_tsvector('english', coalesce(text,'') || ' ' || coalesce(section,'')))")
        op.execute("CREATE INDEX ix_document_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops)")

    for column in (
        sa.Column("notification_number", sa.String(120)), sa.Column("notification_date", sa.Date()),
        sa.Column("effective_until", sa.Date()), sa.Column("supersedes_id", sa.String(64), sa.ForeignKey("qcos.id")),
        sa.Column("superseded_by_id", sa.String(64), sa.ForeignKey("qcos.id")),
        sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id")),
    ):
        op.add_column("qcos", column)
    op.create_index("ix_qcos_notification_number", "qcos", ["notification_number"])
    op.create_table(
        "qco_applicability",
        sa.Column("qco_id", sa.String(64), sa.ForeignKey("qcos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enterprise_category", sa.String(32), nullable=False),
        sa.Column("covered_product_category", sa.String(240), nullable=False),
        sa.Column("standard_reference", sa.String(160), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_until", sa.Date()),
        sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id"), nullable=False),
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("qco_id", "enterprise_category", "covered_product_category", name="uq_qco_applicability"),
    )
    for column in ("qco_id", "enterprise_category", "covered_product_category", "effective_from"):
        op.create_index(f"ix_qco_applicability_{column}", "qco_applicability", [column])

    op.add_column("certification_schemes", sa.Column("qco_id", sa.String(64), sa.ForeignKey("qcos.id")))
    op.add_column("certification_schemes", sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id")))
    op.create_index("ix_certification_schemes_qco_id", "certification_schemes", ["qco_id"])
    op.add_column("tests", sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id")))

    lab_columns = [
        sa.Column("valid_from", sa.Date()), sa.Column("scope_identifier", sa.String(120)), sa.Column("scope", sa.Text()),
        sa.Column("test_clauses", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(32), nullable=False, server_default="UNKNOWN"), sa.Column("source_url", sa.Text()),
        sa.Column("retrieved_at", sa.DateTime(timezone=True)),
        sa.Column("verification_status", sa.String(32), nullable=False, server_default="UNVERIFIED"),
        sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id")),
    ]
    for column in lab_columns:
        op.add_column("laboratory_recognitions", column)
    op.create_index("ix_laboratory_recognitions_status", "laboratory_recognitions", ["status"])
    op.create_index("ix_laboratory_recognitions_verification_status", "laboratory_recognitions", ["verification_status"])

    op.add_column("product_manuals", sa.Column("manual_identifier", sa.String(240)))
    op.add_column("product_manuals", sa.Column("status", sa.String(32), nullable=False, server_default="UNKNOWN"))
    op.add_column("product_manuals", sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id")))
    op.create_index("ix_product_manuals_manual_identifier", "product_manuals", ["manual_identifier"])

    op.add_column("compliance_profiles", sa.Column("as_of_date", sa.Date()))
    op.add_column("compliance_profiles", sa.Column("data_mode", sa.String(24), nullable=False, server_default="DEMO"))
    op.add_column("compliance_profiles", sa.Column("explanation_tree", sa.JSON(), nullable=False, server_default="{}"))
    op.create_index("ix_compliance_profiles_as_of_date", "compliance_profiles", ["as_of_date"])
    op.create_index("ix_compliance_profiles_data_mode", "compliance_profiles", ["data_mode"])
    op.add_column("citations", sa.Column("validation_status", sa.String(32), nullable=False, server_default="PENDING"))
    op.add_column("citations", sa.Column("validation_error", sa.Text()))

    # Normalize the deployed Phase 2A vocabulary without losing demo records.
    for table in ("products", "standards", "documents", "qcos", "certification_schemes", "tests", "laboratories", "laboratory_recognitions", "product_manuals", "compliance_rules", "citations"):
        op.execute(sa.text(f"UPDATE {table} SET source_kind = upper(source_kind)"))


def downgrade() -> None:
    # This migration deliberately keeps a complete downgrade for development databases.
    op.drop_column("citations", "validation_error")
    op.drop_column("citations", "validation_status")
    for name in ("data_mode", "as_of_date"):
        op.drop_index(f"ix_compliance_profiles_{name}", table_name="compliance_profiles")
    for name in ("explanation_tree", "data_mode", "as_of_date"):
        op.drop_column("compliance_profiles", name)
    op.drop_index("ix_product_manuals_manual_identifier", table_name="product_manuals")
    for name in ("source_record_id", "status", "manual_identifier"):
        op.drop_column("product_manuals", name)
    for name in ("verification_status", "status"):
        op.drop_index(f"ix_laboratory_recognitions_{name}", table_name="laboratory_recognitions")
    for name in ("source_record_id", "verification_status", "retrieved_at", "source_url", "status", "test_clauses", "scope", "scope_identifier", "valid_from"):
        op.drop_column("laboratory_recognitions", name)
    op.drop_column("tests", "source_record_id")
    op.drop_index("ix_certification_schemes_qco_id", table_name="certification_schemes")
    op.drop_column("certification_schemes", "source_record_id")
    op.drop_column("certification_schemes", "qco_id")
    op.drop_table("qco_applicability")
    op.drop_index("ix_qcos_notification_number", table_name="qcos")
    for name in ("source_record_id", "superseded_by_id", "supersedes_id", "effective_until", "notification_date", "notification_number"):
        op.drop_column("qcos", name)
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw")
        op.execute("DROP INDEX IF EXISTS ix_document_chunks_fts")
    op.drop_index("ix_document_chunks_content_hash", table_name="document_chunks")
    for name in ("content_hash", "paragraph_index", "table_label", "subclause", "heading"):
        op.drop_column("document_chunks", name)
    for name in ("status", "content_hash", "document_identifier", "verification_status"):
        op.drop_index(f"ix_documents_{name}", table_name="documents")
    for name in ("status", "effective_until", "content_hash", "document_identifier", "verification_status", "source_authority"):
        op.drop_column("documents", name)
    op.drop_table("product_standard_mappings")
    op.drop_table("product_categories")
    op.drop_column("standard_relationships", "source_record_id")
    op.drop_column("standard_relationships", "rationale")
    op.drop_column("product_profiles", "structured_attributes")
    op.drop_table("provenance_links")
    op.drop_table("source_records")
    op.drop_table("ingestion_runs")
