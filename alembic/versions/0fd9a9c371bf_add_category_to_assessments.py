"""add_category_to_assessments

Revision ID: 0fd9a9c371bf
Revises: a96ead64b529
Create Date: 2025-11-24 15:17:35.786053

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fd9a9c371bf'
down_revision = 'a96ead64b529'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add category column to assessments table
    op.add_column('assessments', sa.Column('category', sa.String(length=100), nullable=True))


def downgrade() -> None:
    # Remove category column from assessments table
    op.drop_column('assessments', 'category')
