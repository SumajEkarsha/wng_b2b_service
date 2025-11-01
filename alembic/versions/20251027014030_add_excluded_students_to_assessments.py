"""add excluded_students to assessments

Revision ID: add_excluded_students
Revises: fix_risklevel_enum
Create Date: 2024-10-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_excluded_students'
down_revision = 'fix_risklevel_enum'

def upgrade():
    op.add_column('assessments', sa.Column('excluded_students', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True))

def downgrade():
    op.drop_column('assessments', 'excluded_students')
