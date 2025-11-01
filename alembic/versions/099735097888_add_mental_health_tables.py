"""add_mental_health_tables

Revision ID: 099735097888
Revises: 234475a0b965
Create Date: 2025-10-25 22:24:11.362978

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '099735097888'
down_revision = '234475a0b965'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to students table (check if they exist first)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    students_columns = [col['name'] for col in inspector.get_columns('students')]
    
    if 'roll_number' not in students_columns:
        op.add_column('students', sa.Column('roll_number', sa.String(), nullable=True))
    if 'grade' not in students_columns:
        op.add_column('students', sa.Column('grade', sa.String(), nullable=True))
    if 'risk_level' not in students_columns:
        op.add_column('students', sa.Column('risk_level', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='risklevel'), nullable=True))
    if 'wellbeing_score' not in students_columns:
        op.add_column('students', sa.Column('wellbeing_score', sa.Integer(), nullable=True))
    if 'last_assessment' not in students_columns:
        op.add_column('students', sa.Column('last_assessment', sa.Date(), nullable=True))
    if 'consent_status' not in students_columns:
        op.add_column('students', sa.Column('consent_status', sa.Enum('GRANTED', 'PENDING', 'DENIED', name='consentstatus'), nullable=True))
    if 'notes' not in students_columns:
        op.add_column('students', sa.Column('notes', sa.Text(), nullable=True))

    # Add student_id and completed_at columns to student_responses table
    student_responses_columns = [col['name'] for col in inspector.get_columns('student_responses')]
    
    if 'student_id' not in student_responses_columns:
        op.add_column('student_responses', sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=True))
        op.create_foreign_key('fk_student_responses_student_id', 'student_responses', 'students', ['student_id'], ['student_id'])
    if 'completed_at' not in student_responses_columns:
        op.add_column('student_responses', sa.Column('completed_at', sa.DateTime(), nullable=True))

    # Create activities table
    op.create_table(
        'activities',
        sa.Column('activity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('school_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Enum('MINDFULNESS', 'SOCIAL_SKILLS', 'EMOTIONAL_REGULATION', 'ACADEMIC_SUPPORT', 'TEAM_BUILDING', name='activitytype'), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('target_grades', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('materials', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('instructions', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('objectives', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['school_id'], ['schools.school_id'], ),
        sa.PrimaryKeyConstraint('activity_id')
    )

    # Create risk_alerts table
    op.create_table(
        'risk_alerts',
        sa.Column('alert_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('level', sa.Enum('HIGH', 'CRITICAL', name='alertlevel'), nullable=False),
        sa.Column('type', sa.Enum('BEHAVIORAL', 'ACADEMIC', 'EMOTIONAL', 'SOCIAL', name='alerttype'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('triggers', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('recommendations', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.Enum('NEW', 'IN_REVIEW', 'ESCALATED', 'RESOLVED', name='alertstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ),
        sa.PrimaryKeyConstraint('alert_id')
    )

    # Create ai_recommendations table
    op.create_table(
        'ai_recommendations',
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.Enum('INTERVENTION', 'ASSESSMENT', 'REFERRAL', 'ALERT', name='recommendationtype'), nullable=False),
        sa.Column('confidence', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='confidencelevel'), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.Column('related_student_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('related_case_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_reviewed', sa.Boolean(), nullable=False),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['related_case_id'], ['cases.case_id'], ),
        sa.ForeignKeyConstraint(['related_student_id'], ['students.student_id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('recommendation_id')
    )

    # Create consent_records table
    op.create_table(
        'consent_records',
        sa.Column('consent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_name', sa.String(length=200), nullable=True),
        sa.Column('consent_type', sa.Enum('ASSESSMENT', 'INTERVENTION', 'DATA_SHARING', 'AI_ANALYSIS', name='consenttype'), nullable=False),
        sa.Column('status', sa.Enum('GRANTED', 'PENDING', 'DENIED', 'REVOKED', name='consentstatus_record'), nullable=False),
        sa.Column('granted_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('documents', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ),
        sa.PrimaryKeyConstraint('consent_id')
    )

    # Create goals table
    op.create_table(
        'goals',
        sa.Column('goal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'PAUSED', name='goalstatus'), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.case_id'], ),
        sa.PrimaryKeyConstraint('goal_id')
    )

    # Create daily_boosters table
    op.create_table(
        'daily_boosters',
        sa.Column('booster_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('school_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('type', sa.Enum('STORY', 'PUZZLE', 'MOVEMENT', name='boostertype'), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('purpose', sa.Text(), nullable=True),
        sa.Column('target_grades', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('difficulty', sa.Enum('EASY', 'MEDIUM', 'ENGAGING', name='difficultylevel'), nullable=False),
        sa.Column('full_instructions', sa.Text(), nullable=False),
        sa.Column('materials', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['school_id'], ['schools.school_id'], ),
        sa.PrimaryKeyConstraint('booster_id')
    )

    # Create calendar_events table
    op.create_table(
        'calendar_events',
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('school_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Enum('SESSION', 'ASSESSMENT', 'MEETING', 'ACTIVITY', 'REMINDER', name='eventtype'), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('attendees', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('status', sa.Enum('SCHEDULED', 'COMPLETED', 'CANCELLED', 'RESCHEDULED', name='eventstatus'), nullable=False),
        sa.Column('related_case_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('related_student_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['related_case_id'], ['cases.case_id'], ),
        sa.ForeignKeyConstraint(['related_student_id'], ['students.student_id'], ),
        sa.ForeignKeyConstraint(['school_id'], ['schools.school_id'], ),
        sa.PrimaryKeyConstraint('event_id')
    )

    # Create session_notes table
    op.create_table(
        'session_notes',
        sa.Column('session_note_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('counsellor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('type', sa.Enum('INDIVIDUAL', 'GROUP', 'ASSESSMENT', 'CONSULTATION', name='sessiontype'), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('interventions', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('next_steps', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.case_id'], ),
        sa.ForeignKeyConstraint(['counsellor_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('session_note_id')
    )


def downgrade() -> None:
    # Drop new tables
    op.drop_table('session_notes')
    op.drop_table('calendar_events')
    op.drop_table('daily_boosters')
    op.drop_table('goals')
    op.drop_table('consent_records')
    op.drop_table('ai_recommendations')
    op.drop_table('risk_alerts')
    op.drop_table('activities')

    # Drop new columns from student_responses table
    op.drop_constraint('fk_student_responses_student_id', 'student_responses', type_='foreignkey')
    op.drop_column('student_responses', 'completed_at')
    op.drop_column('student_responses', 'student_id')

    # Drop new columns from students table
    op.drop_column('students', 'notes')
    op.drop_column('students', 'consent_status')
    op.drop_column('students', 'last_assessment')
    op.drop_column('students', 'wellbeing_score')
    op.drop_column('students', 'risk_level')
    op.drop_column('students', 'grade')
    op.drop_column('students', 'roll_number')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS sessiontype')
    op.execute('DROP TYPE IF EXISTS eventstatus')
    op.execute('DROP TYPE IF EXISTS eventtype')
    op.execute('DROP TYPE IF EXISTS difficultylevel')
    op.execute('DROP TYPE IF EXISTS boostertype')
    op.execute('DROP TYPE IF EXISTS goalstatus')
    op.execute('DROP TYPE IF EXISTS consentstatus_record')
    op.execute('DROP TYPE IF EXISTS consenttype')
    op.execute('DROP TYPE IF EXISTS confidencelevel')
    op.execute('DROP TYPE IF EXISTS recommendationtype')
    op.execute('DROP TYPE IF EXISTS alertstatus')
    op.execute('DROP TYPE IF EXISTS alerttype')
    op.execute('DROP TYPE IF EXISTS alertlevel')
    op.execute('DROP TYPE IF EXISTS activitytype')
    op.execute('DROP TYPE IF EXISTS consentstatus')
    op.execute('DROP TYPE IF EXISTS risklevel')
