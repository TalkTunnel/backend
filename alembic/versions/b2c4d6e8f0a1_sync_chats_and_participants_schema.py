"""Add chats.is_encrypted, chats.updated_at, chat_participants.role if missing

Revision ID: b2c4d6e8f0a1
Revises: f3a8b1c2d4e5
Create Date: 2026-03-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c4d6e8f0a1"
down_revision: Union[str, Sequence[str], None] = "f3a8b1c2d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    chat_cols = {c["name"] for c in insp.get_columns("chats")}
    if "is_encrypted" not in chat_cols:
        op.add_column(
            "chats",
            sa.Column(
                "is_encrypted",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )
        op.alter_column("chats", "is_encrypted", server_default=None)
    if "updated_at" not in chat_cols:
        op.add_column("chats", sa.Column("updated_at", sa.DateTime(), nullable=True))
        op.execute("UPDATE chats SET updated_at = created_at WHERE updated_at IS NULL")

    part_cols = {c["name"] for c in insp.get_columns("chat_participants")}
    if "role" not in part_cols:
        op.add_column(
            "chat_participants",
            sa.Column(
                "role",
                sa.String(length=20),
                nullable=False,
                server_default="member",
            ),
        )
        op.alter_column("chat_participants", "role", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    chat_cols = {c["name"] for c in insp.get_columns("chats")}
    part_cols = {c["name"] for c in insp.get_columns("chat_participants")}
    if "role" in part_cols:
        op.drop_column("chat_participants", "role")
    if "updated_at" in chat_cols:
        op.drop_column("chats", "updated_at")
    if "is_encrypted" in chat_cols:
        op.drop_column("chats", "is_encrypted")
