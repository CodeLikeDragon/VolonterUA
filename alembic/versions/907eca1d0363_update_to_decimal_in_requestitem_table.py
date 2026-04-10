"""update to decimal in RequestItem table

Revision ID: 907eca1d0363
Revises: 6396f4becce3
Create Date: 2026-04-02 15:52:44.761550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '907eca1d0363'
down_revision: Union[str, Sequence[str], None] = '6396f4becce3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. assigned_qty → Numeric
    op.alter_column(
        'request_items',
        'assigned_qty',
        existing_type=sa.Float(),
        type_=sa.Numeric(precision=12, scale=3),
        postgresql_using='assigned_qty::numeric'
    )

    # 2. qty → NOT NULL (якщо потрібно)
    op.alter_column(
        'request_items',
        'qty',
        existing_type=sa.NUMERIC(precision=12, scale=3),
        nullable=False
    )


def downgrade() -> None:
    # назад у float
    op.alter_column(
        'request_items',
        'assigned_qty',
        existing_type=sa.Numeric(precision=12, scale=3),
        type_=sa.Float(),
        postgresql_using='assigned_qty::float'
    )

    op.alter_column(
        'request_items',
        'qty',
        existing_type=sa.NUMERIC(precision=12, scale=3),
        nullable=True
    )
