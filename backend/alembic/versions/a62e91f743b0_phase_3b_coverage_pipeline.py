"""Add scalable product-family coverage workflow.

Revision ID: a62e91f743b0
Revises: f3c8a1d2e740
"""
from alembic import op
import sqlalchemy as sa

revision = "a62e91f743b0"
down_revision = "f3c8a1d2e740"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("coverage_records", sa.Column("lifecycle_status", sa.String(32), nullable=False, server_default="PUBLISHED"))
    op.add_column("coverage_records", sa.Column("completeness_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")))
    op.add_column("coverage_records", sa.Column("lab_completeness", sa.String(32), nullable=False, server_default="UNKNOWN"))
    op.add_column("coverage_records", sa.Column("reviewed_by", sa.String(160)))
    op.add_column("coverage_records", sa.Column("reviewed_at", sa.DateTime(timezone=True)))
    op.add_column("coverage_records", sa.Column("published_at", sa.DateTime(timezone=True)))
    op.add_column("coverage_records", sa.Column("last_refreshed_at", sa.DateTime(timezone=True)))
    op.create_index("ix_coverage_records_lifecycle_status", "coverage_records", ["lifecycle_status"])
    op.create_index("ix_coverage_records_lab_completeness", "coverage_records", ["lab_completeness"])

    op.create_table(
        "product_families",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("name", sa.String(240), nullable=False),
        sa.Column("product_group", sa.String(120), nullable=False),
        sa.Column("product_category_id", sa.String(64), sa.ForeignKey("product_categories.id")),
        sa.Column("aliases", sa.JSON(), nullable=False),
        sa.Column("required_attributes", sa.JSON(), nullable=False),
        sa.Column("optional_attributes", sa.JSON(), nullable=False),
        sa.Column("ambiguity_terms", sa.JSON(), nullable=False),
        sa.Column("lifecycle_status", sa.String(32), nullable=False, server_default="DISCOVERED"),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("reviewed_by", sa.String(160)),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_product_families_slug", "product_families", ["slug"])
    op.create_index("ix_product_families_name", "product_families", ["name"])
    op.create_index("ix_product_families_product_group", "product_families", ["product_group"])
    op.create_index("ix_product_families_product_category_id", "product_families", ["product_category_id"])
    op.create_index("ix_product_families_lifecycle_status", "product_families", ["lifecycle_status"])

    op.create_table(
        "source_family_impacts",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_record_id", sa.String(64), sa.ForeignKey("source_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_family_id", sa.String(64), sa.ForeignKey("product_families.id", ondelete="CASCADE"), nullable=False),
        sa.Column("impact_type", sa.String(48), nullable=False),
        sa.Column("relationship_note", sa.Text()),
        sa.UniqueConstraint("source_record_id", "product_family_id", "impact_type", name="uq_source_family_impact"),
    )
    op.create_index("ix_source_family_impacts_source_record_id", "source_family_impacts", ["source_record_id"])
    op.create_index("ix_source_family_impacts_product_family_id", "source_family_impacts", ["product_family_id"])
    op.create_index("ix_source_family_impacts_impact_type", "source_family_impacts", ["impact_type"])


def downgrade() -> None:
    op.drop_table("source_family_impacts")
    op.drop_table("product_families")
    op.drop_index("ix_coverage_records_lab_completeness", table_name="coverage_records")
    op.drop_index("ix_coverage_records_lifecycle_status", table_name="coverage_records")
    for name in ("last_refreshed_at", "published_at", "reviewed_at", "reviewed_by", "lab_completeness", "completeness_json", "lifecycle_status"):
        op.drop_column("coverage_records", name)
