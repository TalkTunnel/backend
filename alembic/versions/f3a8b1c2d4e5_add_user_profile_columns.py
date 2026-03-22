"""Add user profile columns (full_name, bio, avatar_url, is_verified)

Revision ID: f3a8b1c2d4e5
Revises: 06920332f8bc
Create Date: 2026-03-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f3a8b1c2d4e5"
down_revision: Union[str, Sequence[str], None] = "06920332f8bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing = {c["name"] for c in insp.get_columns("users")}

    if "full_name" not in existing:
        op.add_column("users", sa.Column("full_name", sa.String(length=100), nullable=True))
    if "bio" not in existing:
        op.add_column("users", sa.Column("bio", sa.String(length=500), nullable=True))
    if "avatar_url" not in existing:
        op.add_column("users", sa.Column("avatar_url", sa.String(length=500), nullable=True))
    if "is_verified" not in existing:
        op.add_column(
            "users",
            sa.Column(
                "is_verified",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
        op.alter_column("users", "is_verified", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "is_verified")
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "bio")
    op.drop_column("users", "full_name")
