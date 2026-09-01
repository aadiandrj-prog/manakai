"""separate demo and authoritative standard identities

Revision ID: 7a91d3e5f620
Revises: 4b2f2a8d1c71
"""
from typing import Sequence, Union

from alembic import op


revision: str = "7a91d3e5f620"
down_revision: Union[str, None] = "4b2f2a8d1c71"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("uq_standard_number_version", "standards", type_="unique")
    op.create_unique_constraint("uq_standard_number_version_source", "standards", ["number", "version", "source_kind"])


def downgrade() -> None:
    op.drop_constraint("uq_standard_number_version_source", "standards", type_="unique")
    op.create_unique_constraint("uq_standard_number_version", "standards", ["number", "version"])
