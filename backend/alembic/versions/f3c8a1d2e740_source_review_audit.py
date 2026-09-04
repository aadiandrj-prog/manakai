"""Add auditable source-change review resolution.

Revision ID: f3c8a1d2e740
Revises: d7e2c9a4f610
"""
from alembic import op
import sqlalchemy as sa

revision = "f3c8a1d2e740"
down_revision = "d7e2c9a4f610"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("source_change_events", sa.Column("reviewed_at", sa.DateTime(timezone=True)))
    op.add_column("source_change_events", sa.Column("reviewed_by", sa.String(160)))
    op.add_column("source_change_events", sa.Column("review_note", sa.Text()))
    op.add_column("source_change_events", sa.Column("canonical_source_record_id", sa.String(64), sa.ForeignKey("source_records.id")))
    op.create_index("ix_source_change_events_canonical_source_record_id", "source_change_events", ["canonical_source_record_id"])


def downgrade() -> None:
    op.drop_index("ix_source_change_events_canonical_source_record_id", table_name="source_change_events")
    op.drop_column("source_change_events", "canonical_source_record_id")
    op.drop_column("source_change_events", "review_note")
    op.drop_column("source_change_events", "reviewed_by")
    op.drop_column("source_change_events", "reviewed_at")
