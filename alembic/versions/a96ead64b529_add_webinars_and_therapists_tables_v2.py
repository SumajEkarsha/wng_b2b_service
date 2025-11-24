"""add webinars and therapists tables v2

Revision ID: a96ead64b529
Revises: eb9cdc59dffc
Create Date: 2025-11-24 01:52:57.309520

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'a96ead64b529'
down_revision = 'eb9cdc59dffc'  # Changed to skip the problematic migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums only if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE webinarcategory AS ENUM ('Student Wellbeing', 'Mental Health', 'Crisis Management', 'Professional Development', 'Communication', 'Self-Care', 'Safety', 'Learning Disabilities', 'Counseling Skills', 'Curriculum', 'Inclusion');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE webinarstatus AS ENUM ('Upcoming', 'Live', 'Recorded', 'Cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE webinarlevel AS ENUM ('Beginner', 'Intermediate', 'Advanced', 'All Levels');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE registrationstatus AS ENUM ('Registered', 'Attended', 'Cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE availabilitystatus AS ENUM ('Available', 'Limited', 'Unavailable');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE bookingstatus AS ENUM ('Requested', 'Confirmed', 'Cancelled', 'Completed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    
    # Create webinars table
    op.create_table(
        'webinars',
        sa.Column('webinar_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('speaker_name', sa.String(), nullable=False),
        sa.Column('speaker_title', sa.String(), nullable=True),
        sa.Column('speaker_bio', sa.Text(), nullable=True),
        sa.Column('speaker_image_url', sa.String(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('category', sa.Enum('Student Wellbeing', 'Mental Health', 'Crisis Management', 'Professional Development', 'Communication', 'Self-Care', 'Safety', 'Learning Disabilities', 'Counseling Skills', 'Curriculum', 'Inclusion', name='webinarcategory'), nullable=False),
        sa.Column('status', sa.Enum('Upcoming', 'Live', 'Recorded', 'Cancelled', name='webinarstatus'), nullable=False),
        sa.Column('level', sa.Enum('Beginner', 'Intermediate', 'Advanced', 'All Levels', name='webinarlevel'), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('topics', postgresql.JSON(), nullable=True),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('max_attendees', sa.Integer(), nullable=True),
        sa.Column('attendee_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('webinar_id')
    )
    op.create_index('ix_webinars_title', 'webinars', ['title'])
    op.create_index('ix_webinars_date', 'webinars', ['date'])
    op.create_index('ix_webinars_category', 'webinars', ['category'])
    op.create_index('ix_webinars_status', 'webinars', ['status'])
    
    # Create webinar_registrations table
    op.create_table(
        'webinar_registrations',
        sa.Column('registration_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('webinar_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('Registered', 'Attended', 'Cancelled', name='registrationstatus'), nullable=False),
        sa.Column('registered_at', sa.DateTime(), nullable=True),
        sa.Column('attended_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['webinar_id'], ['webinars.webinar_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('registration_id')
    )
    op.create_index('ix_webinar_registrations_webinar_id', 'webinar_registrations', ['webinar_id'])
    op.create_index('ix_webinar_registrations_user_id', 'webinar_registrations', ['user_id'])
    
    # Create therapists table
    op.create_table(
        'therapists',
        sa.Column('therapist_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('specialty', sa.String(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('rating', sa.Numeric(3, 2), nullable=False),
        sa.Column('review_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('distance_km', sa.Numeric(10, 2), nullable=True),
        sa.Column('experience_years', sa.Integer(), nullable=False),
        sa.Column('languages', postgresql.JSON(), nullable=False),
        sa.Column('availability_status', sa.Enum('Available', 'Limited', 'Unavailable', name='availabilitystatus'), nullable=False),
        sa.Column('consultation_fee_min', sa.Numeric(10, 2), nullable=False),
        sa.Column('consultation_fee_max', sa.Numeric(10, 2), nullable=False),
        sa.Column('qualifications', postgresql.JSON(), nullable=True),
        sa.Column('areas_of_expertise', postgresql.JSON(), nullable=True),
        sa.Column('profile_image_url', sa.String(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('therapist_id')
    )
    op.create_index('ix_therapists_name', 'therapists', ['name'])
    op.create_index('ix_therapists_specialty', 'therapists', ['specialty'])
    op.create_index('ix_therapists_location', 'therapists', ['location'])
    op.create_index('ix_therapists_city', 'therapists', ['city'])
    op.create_index('ix_therapists_availability_status', 'therapists', ['availability_status'])
    
    # Create therapist_bookings table
    op.create_table(
        'therapist_bookings',
        sa.Column('booking_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('therapist_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('appointment_date', sa.Date(), nullable=False),
        sa.Column('appointment_time', sa.Time(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('Requested', 'Confirmed', 'Cancelled', 'Completed', name='bookingstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['therapist_id'], ['therapists.therapist_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('booking_id')
    )
    op.create_index('ix_therapist_bookings_therapist_id', 'therapist_bookings', ['therapist_id'])
    op.create_index('ix_therapist_bookings_user_id', 'therapist_bookings', ['user_id'])
    op.create_index('ix_therapist_bookings_student_id', 'therapist_bookings', ['student_id'])
    op.create_index('ix_therapist_bookings_appointment_date', 'therapist_bookings', ['appointment_date'])
    op.create_index('ix_therapist_bookings_status', 'therapist_bookings', ['status'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('therapist_bookings')
    op.drop_table('therapists')
    op.drop_table('webinar_registrations')
    op.drop_table('webinars')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS bookingstatus')
    op.execute('DROP TYPE IF EXISTS availabilitystatus')
    op.execute('DROP TYPE IF EXISTS registrationstatus')
    op.execute('DROP TYPE IF EXISTS webinarlevel')
    op.execute('DROP TYPE IF EXISTS webinarstatus')
    op.execute('DROP TYPE IF EXISTS webinarcategory')
