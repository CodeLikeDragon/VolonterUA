"""add categories and request categories

Revision ID: fdc2a5e9a1b4
Revises: 652296ece2d2
Create Date: 2026-08-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "fdc2a5e9a1b4"
down_revision: Union[str, Sequence[str], None] = "652296ece2d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("slug", sa.String(length=55), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
        sa.UniqueConstraint("name", name=op.f("uq_categories_name")),
        sa.UniqueConstraint("slug", name=op.f("uq_categories_slug")),
    )
    op.create_table(
        "request_categories",
        sa.Column("request_id", sa.UUID(), nullable=False),
        sa.Column("category_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name=op.f("fk_request_categories_category_id_categories"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["requests.id"],
            name=op.f("fk_request_categories_request_id_requests"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("request_id", "category_id", name=op.f("pk_request_categories")),
    )
    op.create_index(
        "ix_request_categories_category_id",
        "request_categories",
        ["category_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_request_categories_category_id", table_name="request_categories")
    op.drop_table("request_categories")
    op.drop_table("categories")
