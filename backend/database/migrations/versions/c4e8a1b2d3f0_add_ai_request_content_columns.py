"""add ai request content columns

Revision ID: c4e8a1b2d3f0
Revises: b9cf0a9a471a
Create Date: 2026-07-03 08:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4e8a1b2d3f0"
down_revision: Union[str, None] = "b9cf0a9a471a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ai_requests", sa.Column("user_message", sa.Text(), nullable=True))
    op.add_column("ai_requests", sa.Column("ai_response", sa.Text(), nullable=True))
    op.add_column("ai_requests", sa.Column("response_mode", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("ai_requests", "response_mode")
    op.drop_column("ai_requests", "ai_response")
    op.drop_column("ai_requests", "user_message")
