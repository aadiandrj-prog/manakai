"""Phase 2E multi-vertical coverage and hallmarking regime.

Revision ID: d7e2c9a4f610
Revises: b48f761da923
"""
from alembic import op
import sqlalchemy as sa

revision = "d7e2c9a4f610"
down_revision = "b48f761da923"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("source_records", sa.Column("review_status", sa.String(32), nullable=False, server_default="VERIFIED"))
    op.create_index("ix_source_records_review_status", "source_records", ["review_status"])
    op.add_column("source_change_events", sa.Column("change_classification", sa.String(32), nullable=False, server_default="UNKNOWN"))
    op.add_column("source_change_events", sa.Column("review_status", sa.String(32), nullable=False, server_default="PENDING"))
    op.add_column("source_change_events", sa.Column("changed_fields", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("source_change_events", sa.Column("material_summary", sa.Text()))
    op.create_index("ix_source_change_events_change_classification", "source_change_events", ["change_classification"])
    op.create_index("ix_source_change_events_review_status", "source_change_events", ["review_status"])
    op.create_table("regulatory_regimes",
        sa.Column("id", sa.String(64), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False, unique=True), sa.Column("name", sa.String(240), nullable=False),
        sa.Column("regime_type", sa.String(48), nullable=False), sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_kind", sa.String(24), nullable=False), sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id")),
        sa.Column("journey_template", sa.JSON(), nullable=False))
    op.create_index("ix_regulatory_regimes_slug", "regulatory_regimes", ["slug"], unique=True)
    op.create_index("ix_regulatory_regimes_regime_type", "regulatory_regimes", ["regime_type"])
    op.create_index("ix_regulatory_regimes_source_kind", "regulatory_regimes", ["source_kind"])
    op.create_table("coverage_records",
        sa.Column("id", sa.String(64), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("product_category_id", sa.String(64), sa.ForeignKey("product_categories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("primary_standard_id", sa.String(64), sa.ForeignKey("standards.id")), sa.Column("regime_id", sa.String(64), sa.ForeignKey("regulatory_regimes.id")),
        sa.Column("coverage_status", sa.String(32), nullable=False), sa.Column("coverage_reason", sa.Text(), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True)), sa.Column("authoritative_sources_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("known_limitations", sa.JSON(), nullable=False, server_default="[]"), sa.Column("standard_metadata_available", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("compliance_verified", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.UniqueConstraint("product_category_id", "primary_standard_id", name="uq_coverage_category_standard"))
    for column in ("product_category_id", "primary_standard_id", "regime_id", "coverage_status"):
        op.create_index(f"ix_coverage_records_{column}", "coverage_records", [column])
    op.create_table("test_standard_relationships",
        sa.Column("id", sa.String(64), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("test_id", sa.String(64), sa.ForeignKey("tests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("referenced_standard_id", sa.String(64), sa.ForeignKey("standards.id"), nullable=False),
        sa.Column("relationship_type", sa.String(48), nullable=False), sa.Column("rationale", sa.Text()),
        sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id")),
        sa.UniqueConstraint("test_id", "referenced_standard_id", name="uq_test_referenced_standard"))
    op.create_index("ix_test_standard_relationships_test_id", "test_standard_relationships", ["test_id"])
    op.create_index("ix_test_standard_relationships_referenced_standard_id", "test_standard_relationships", ["referenced_standard_id"])
    op.add_column("laboratory_recognitions", sa.Column("grade_type", sa.Text()))
    op.add_column("laboratory_recognitions", sa.Column("testing_charge", sa.String(120)))
    op.add_column("laboratory_recognitions", sa.Column("remark", sa.Text()))
    op.add_column("laboratory_recognitions", sa.Column("completeness_warning", sa.Text()))
    op.add_column("product_manuals", sa.Column("supersedes_id", sa.String(64), sa.ForeignKey("product_manuals.id")))
    op.add_column("product_manuals", sa.Column("superseded_by_id", sa.String(64), sa.ForeignKey("product_manuals.id")))
    op.create_table("hallmarking_centres",
        sa.Column("id", sa.String(64), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("name", sa.String(300), nullable=False), sa.Column("centre_identifier", sa.String(120), unique=True),
        sa.Column("address", sa.Text()), sa.Column("city", sa.String(120)), sa.Column("state", sa.String(120)),
        sa.Column("status", sa.String(32), nullable=False), sa.Column("valid_from", sa.Date()), sa.Column("valid_until", sa.Date()),
        sa.Column("scope", sa.Text()), sa.Column("source_url", sa.Text(), nullable=False), sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_kind", sa.String(24), nullable=False), sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id")),
        sa.Column("warning", sa.Text()))
    for column in ("name", "centre_identifier", "city", "state", "status", "source_kind"):
        op.create_index(f"ix_hallmarking_centres_{column}", "hallmarking_centres", [column], unique=column == "centre_identifier")
    op.create_table("hallmarking_guidance",
        sa.Column("id", sa.String(64), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("topic", sa.String(120), nullable=False, unique=True), sa.Column("title", sa.String(240), nullable=False),
        sa.Column("guidance", sa.JSON(), nullable=False), sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_kind", sa.String(24), nullable=False), sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id")))
    op.create_index("ix_hallmarking_guidance_topic", "hallmarking_guidance", ["topic"], unique=True)
    op.add_column("compliance_profiles", sa.Column("coverage_id", sa.String(64), sa.ForeignKey("coverage_records.id")))
    op.add_column("compliance_profiles", sa.Column("regime_id", sa.String(64), sa.ForeignKey("regulatory_regimes.id")))
    op.create_index("ix_compliance_profiles_coverage_id", "compliance_profiles", ["coverage_id"])
    op.create_index("ix_compliance_profiles_regime_id", "compliance_profiles", ["regime_id"])


def downgrade() -> None:
    op.drop_index("ix_compliance_profiles_regime_id", table_name="compliance_profiles"); op.drop_index("ix_compliance_profiles_coverage_id", table_name="compliance_profiles")
    op.drop_column("compliance_profiles", "regime_id"); op.drop_column("compliance_profiles", "coverage_id")
    op.drop_table("hallmarking_guidance"); op.drop_table("hallmarking_centres")
    op.drop_column("product_manuals", "superseded_by_id"); op.drop_column("product_manuals", "supersedes_id")
    for column in ("completeness_warning", "remark", "testing_charge", "grade_type"):
        op.drop_column("laboratory_recognitions", column)
    op.drop_table("test_standard_relationships"); op.drop_table("coverage_records"); op.drop_table("regulatory_regimes")
    op.drop_column("source_change_events", "material_summary"); op.drop_column("source_change_events", "changed_fields")
    op.drop_index("ix_source_change_events_review_status", table_name="source_change_events"); op.drop_column("source_change_events", "review_status")
    op.drop_index("ix_source_change_events_change_classification", table_name="source_change_events"); op.drop_column("source_change_events", "change_classification")
    op.drop_index("ix_source_records_review_status", table_name="source_records"); op.drop_column("source_records", "review_status")
