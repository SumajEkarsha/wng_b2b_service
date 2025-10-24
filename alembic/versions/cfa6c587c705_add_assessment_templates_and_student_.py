"""add_assessment_templates_and_student_responses_tables

Revision ID: cfa6c587c705
Revises: 12485645a6b4
Create Date: 2025-10-24 23:20:37.730535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfa6c587c705'
down_revision = '12485645a6b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create assessment_templates table
    op.create_table(
        'assessment_templates',
        sa.Column('template_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('questions', sa.JSON(), nullable=False),
        sa.Column('scoring_rules', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('template_id')
    )

    # Create student_responses table
    op.create_table(
        'student_responses',
        sa.Column('response_id', sa.UUID(), nullable=False),
        sa.Column('assessment_id', sa.UUID(), nullable=False),
        sa.Column('question_id', sa.String(length=100), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('answer', sa.JSON(), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.assessment_id'], ),
        sa.PrimaryKeyConstraint('response_id')
    )

    # Update assessments table
    # First, delete all existing assessments (old data structure can't be migrated)
    op.execute("DELETE FROM assessments")
    
    # Drop old columns
    op.drop_column('assessments', 'responses')
    op.drop_column('assessments', 'scores')
    
    # Add new columns
    op.add_column('assessments', sa.Column('total_score', sa.Float(), nullable=True))
    op.add_column('assessments', sa.Column('notes', sa.Text(), nullable=True))
    
    # Make template_id required and add foreign key
    op.alter_column('assessments', 'template_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.create_foreign_key(None, 'assessments', 'assessment_templates', ['template_id'], ['template_id'])


def downgrade() -> None:
    # Remove foreign key from assessments
    op.drop_constraint(None, 'assessments', type_='foreignkey')
    
    # Revert assessments table changes
    op.alter_column('assessments', 'template_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_column('assessments', 'notes')
    op.drop_column('assessments', 'total_score')
    op.add_column('assessments', sa.Column('scores', sa.JSON(), nullable=True))
    op.add_column('assessments', sa.Column('responses', sa.JSON(), nullable=True))
    
    # Drop new tables
    op.drop_table('student_responses')
    op.drop_table('assessment_templates')
