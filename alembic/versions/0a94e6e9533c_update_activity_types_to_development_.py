"""update_activity_types_to_development_categories

Revision ID: 0a94e6e9533c
Revises: d155c07ce201
Create Date: 2025-11-28 17:26:11.430331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a94e6e9533c'
down_revision = 'd155c07ce201'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First, migrate existing activity types to the new ones
    # Map old types to new development-focused types
    op.execute("""
        UPDATE activities 
        SET type = 'PHYSICAL_DEVELOPMENT'
        WHERE type IN ('MINDFULNESS', 'TEAM_BUILDING');
    """)
    
    op.execute("""
        UPDATE activities 
        SET type = 'COGNITIVE_DEVELOPMENT'
        WHERE type = 'ACADEMIC_SUPPORT';
    """)
    
    op.execute("""
        UPDATE activities 
        SET type = 'SOCIAL_EMOTIONAL_DEVELOPMENT'
        WHERE type IN ('SOCIAL_SKILLS', 'EMOTIONAL_REGULATION');
    """)
    
    # Drop the old enum type and create new one
    op.execute("ALTER TYPE activitytype RENAME TO activitytype_old")
    
    # Create new enum type with only development categories
    op.execute("""
        CREATE TYPE activitytype AS ENUM (
            'PHYSICAL_DEVELOPMENT',
            'COGNITIVE_DEVELOPMENT',
            'SOCIAL_EMOTIONAL_DEVELOPMENT',
            'LANGUAGE_COMMUNICATION_DEVELOPMENT'
        )
    """)
    
    # Update the column to use the new enum type
    op.execute("""
        ALTER TABLE activities 
        ALTER COLUMN type TYPE activitytype 
        USING type::text::activitytype
    """)
    
    # Drop the old enum type
    op.execute("DROP TYPE activitytype_old")


def downgrade() -> None:
    # Recreate old enum type
    op.execute("ALTER TYPE activitytype RENAME TO activitytype_new")
    
    op.execute("""
        CREATE TYPE activitytype AS ENUM (
            'MINDFULNESS',
            'SOCIAL_SKILLS',
            'EMOTIONAL_REGULATION',
            'ACADEMIC_SUPPORT',
            'TEAM_BUILDING',
            'SOCIAL_EMOTIONAL_DEVELOPMENT',
            'PHYSICAL_DEVELOPMENT',
            'COGNITIVE_DEVELOPMENT',
            'LANGUAGE_COMMUNICATION_DEVELOPMENT'
        )
    """)
    
    # Migrate data back to old types (approximate mapping)
    op.execute("""
        UPDATE activities 
        SET type = 'MINDFULNESS'::text::activitytype_new
        WHERE type::text = 'PHYSICAL_DEVELOPMENT'
    """)
    
    op.execute("""
        UPDATE activities 
        SET type = 'ACADEMIC_SUPPORT'::text::activitytype_new
        WHERE type::text = 'COGNITIVE_DEVELOPMENT'
    """)
    
    op.execute("""
        UPDATE activities 
        SET type = 'SOCIAL_SKILLS'::text::activitytype_new
        WHERE type::text = 'SOCIAL_EMOTIONAL_DEVELOPMENT'
    """)
    
    # Update column to use old enum
    op.execute("""
        ALTER TABLE activities 
        ALTER COLUMN type TYPE activitytype 
        USING type::text::activitytype
    """)
    
    # Drop new enum
    op.execute("DROP TYPE activitytype_new")
