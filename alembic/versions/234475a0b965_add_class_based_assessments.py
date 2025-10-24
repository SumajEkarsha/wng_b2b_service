"""add_class_based_assessments

Revision ID: 234475a0b965
Revises: 8bfe8db84024
Create Date: 2025-10-25 00:50:56.161636

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '234475a0b965'
down_revision = '8bfe8db84024'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add class_id to assessments (optional - can assign assessment to entire class)
    op.add_column('assessments', sa.Column('class_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_assessments_class_id', 'assessments', 'classes', ['class_id'], ['class_id'])
    
    # 2. Add title to assessments
    op.add_column('assessments', sa.Column('title', sa.String(length=200), nullable=True))
    
    # 3. Add student_id to student_responses (temporarily nullable)
    op.add_column('student_responses', sa.Column('student_id', sa.UUID(), nullable=True))
    
    # 4. Populate student_id in student_responses from assessments table
    op.execute("""
        UPDATE student_responses sr
        SET student_id = (
            SELECT a.student_id 
            FROM assessments a
            WHERE a.assessment_id = sr.assessment_id
        )
    """)
    
    # 5. Make student_id non-nullable and add foreign key
    op.alter_column('student_responses', 'student_id', nullable=False)
    op.create_foreign_key('fk_student_responses_student_id', 'student_responses', 'students', ['student_id'], ['student_id'])
    
    # 6. Add completed_at to student_responses
    op.add_column('student_responses', sa.Column('completed_at', sa.DateTime(), nullable=True))
    
    # 7. Populate completed_at in student_responses from assessments
    op.execute("""
        UPDATE student_responses sr
        SET completed_at = (
            SELECT a.completed_at 
            FROM assessments a
            WHERE a.assessment_id = sr.assessment_id
        )
    """)
    
    # 8. Remove old columns from assessments
    op.drop_column('assessments', 'student_id')
    op.drop_column('assessments', 'completed_at')
    op.drop_column('assessments', 'total_score')


def downgrade() -> None:
    # Reverse the changes
    
    # 1. Re-add columns to assessments
    op.add_column('assessments', sa.Column('total_score', sa.Float(), nullable=True))
    op.add_column('assessments', sa.Column('completed_at', sa.DateTime(), nullable=True))
    op.add_column('assessments', sa.Column('student_id', sa.UUID(), nullable=True))
    
    # 2. Populate from student_responses (take first student's data)
    op.execute("""
        UPDATE assessments a
        SET 
            student_id = (SELECT student_id FROM student_responses WHERE assessment_id = a.assessment_id LIMIT 1),
            completed_at = (SELECT completed_at FROM student_responses WHERE assessment_id = a.assessment_id LIMIT 1),
            total_score = (SELECT SUM(score) FROM student_responses WHERE assessment_id = a.assessment_id)
    """)
    
    # 3. Remove completed_at from student_responses
    op.drop_column('student_responses', 'completed_at')
    
    # 4. Drop student_id foreign key and column from student_responses
    op.drop_constraint('fk_student_responses_student_id', 'student_responses', type_='foreignkey')
    op.drop_column('student_responses', 'student_id')
    
    # 5. Drop title from assessments
    op.drop_column('assessments', 'title')
    
    # 6. Drop class_id from assessments
    op.drop_constraint('fk_assessments_class_id', 'assessments', type_='foreignkey')
    op.drop_column('assessments', 'class_id')
