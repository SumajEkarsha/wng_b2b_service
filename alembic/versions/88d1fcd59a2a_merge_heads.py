"""Merge heads

Revision ID: 88d1fcd59a2a
Revises: add_activity_assignments, c32962455bda
Create Date: 2025-11-28 10:56:47.398861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88d1fcd59a2a'
down_revision = ('add_activity_assignments', 'c32962455bda')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
