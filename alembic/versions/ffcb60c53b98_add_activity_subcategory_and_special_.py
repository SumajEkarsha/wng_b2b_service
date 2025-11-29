"""add_activity_subcategory_and_special_diagnosis

Revision ID: ffcb60c53b98
Revises: 0fd9a9c371bf
Create Date: 2025-11-25 12:41:12.327862

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ffcb60c53b98'
down_revision = 'd155c07ce201'  # Updated to resolve cycle
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add diagnosis column to activities table
    op.add_column('activities', sa.Column('diagnosis', postgresql.ARRAY(sa.String()), nullable=True))


def downgrade() -> None:
    # Remove diagnosis column from activities table
    op.drop_column('activities', 'diagnosis')

