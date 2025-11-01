"""add_requested_status_to_calendar_events

Revision ID: eb9cdc59dffc
Revises: add_excluded_students
Create Date: 2025-10-29 10:03:52.596917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb9cdc59dffc'
down_revision = 'add_excluded_students'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add REQUESTED to the EventStatus enum
    op.execute("ALTER TYPE eventstatus ADD VALUE IF NOT EXISTS 'REQUESTED' BEFORE 'SCHEDULED'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum type
    pass
