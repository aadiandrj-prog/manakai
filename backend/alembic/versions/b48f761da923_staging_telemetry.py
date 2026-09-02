"""add staging AI usage and source change telemetry

Revision ID: b48f761da923
Revises: 91c3d7e2a4b8
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b48f761da923"
down_revision: Union[str, None] = "91c3d7e2a4b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_usage_events",
        sa.Column("provider", sa.String(32), nullable=False), sa.Column("model", sa.String(120)),
        sa.Column("operation", sa.String(48), nullable=False), sa.Column("status", sa.String(32), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False), sa.Column("input_tokens", sa.Integer()),
        sa.Column("output_tokens", sa.Integer()), sa.Column("request_id", sa.String(64)),
        sa.Column("conversation_id", sa.String(64)), sa.Column("validation_result", sa.String(32)),
        sa.Column("validation_reason", sa.String(240)), sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    for column in ("provider", "model", "operation", "status", "request_id", "conversation_id", "validation_result"):
        op.create_index(f"ix_ai_usage_events_{column}", "ai_usage_events", [column])
    op.create_table(
        "source_change_events",
        sa.Column("source_url", sa.Text(), nullable=False), sa.Column("source_type", sa.String(80), nullable=False),
        sa.Column("previous_hash", sa.String(64), nullable=False), sa.Column("new_hash", sa.String(64), nullable=False),
        sa.Column("ingestion_run_id", sa.String(64)), sa.Column("status", sa.String(32), nullable=False),
        sa.Column("id", sa.String(64), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    for column in ("source_type", "ingestion_run_id", "status"):
        op.create_index(f"ix_source_change_events_{column}", "source_change_events", [column])


def downgrade() -> None:
    op.drop_table("source_change_events")
    op.drop_table("ai_usage_events")
