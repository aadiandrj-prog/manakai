"""add controlled AI conversation state

Revision ID: 91c3d7e2a4b8
Revises: 7a91d3e5f620
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "91c3d7e2a4b8"
down_revision: Union[str, None] = "7a91d3e5f620"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("detected_language", sa.String(16), nullable=False, server_default="en"),
        sa.Column("current_intent", sa.String(48), nullable=False, server_default="UNKNOWN"),
        sa.Column("structured_state", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("unresolved_attributes", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("active_compliance_profile_id", sa.String(64)),
        sa.Column("relevant_standard_id", sa.String(64)),
        sa.Column("evidence_references", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_conversations_current_intent", "conversations", ["current_intent"])
    op.create_index("ix_conversations_active_compliance_profile_id", "conversations", ["active_compliance_profile_id"])
    op.create_index("ix_conversations_relevant_standard_id", "conversations", ["relevant_standard_id"])
    op.create_table(
        "conversation_messages",
        sa.Column("conversation_id", sa.String(64), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("language", sa.String(16), nullable=False, server_default="en"),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_conversation_messages_conversation_id", "conversation_messages", ["conversation_id"])
    op.create_index("ix_conversation_messages_role", "conversation_messages", ["role"])


def downgrade() -> None:
    op.drop_table("conversation_messages")
    op.drop_table("conversations")
