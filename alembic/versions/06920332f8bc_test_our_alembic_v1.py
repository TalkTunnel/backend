"""Test our alembic v1

Revision ID: 06920332f8bc
Revises: 9ae4b4c847b8
Create Date: 2026-03-22 21:40:30.837707

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '06920332f8bc'
down_revision: Union[str, Sequence[str], None] = '9ae4b4c847b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Схема уже создана в 9ae4b4c847b8 через Base.metadata.create_all()."""
    pass


def downgrade() -> None:
    """Откат таблиц выполняется в 9ae4b4c847b8 (drop_all), не здесь."""
    pass
