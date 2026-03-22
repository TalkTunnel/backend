"""First create our database

Revision ID: 9ae4b4c847b8
Revises: 
Create Date: 2026-03-22 21:23:57.941746

"""
from typing import Sequence, Union

from alembic import op

import src.models  # noqa: F401
from src.core.database import Base


# revision identifiers, used by Alembic.
revision: str = '9ae4b4c847b8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
