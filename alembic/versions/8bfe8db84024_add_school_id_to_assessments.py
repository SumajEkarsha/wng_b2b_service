"""add_school_id_to_assessments

Revision ID: 8bfe8db84024
Revises: cfa6c587c705
Create Date: 2025-10-25 00:33:16.233078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bfe8db84024'
down_revision = 'cfa6c587c705'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add school_id column to assessments table
    op.add_column('assessments', sa.Column('school_id', sa.UUID(), nullable=True))
    
    # Populate school_id from students table for existing assessments
    op.execute("""
        UPDATE assessments 
        SET school_id = students.school_id 
        FROM students 
        WHERE assessments.student_id = students.student_id
    """)
    
    # Make school_id non-nullable after population
    op.alter_column('assessments', 'school_id', nullable=False)
    
    # Add foreign key constraint
    op.create_foreign_key('fk_assessments_school_id', 'assessments', 'schools', ['school_id'], ['school_id'])


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_assessments_school_id', 'assessments', type_='foreignkey')
    
    # Drop school_id column
    op.drop_column('assessments', 'school_id')
