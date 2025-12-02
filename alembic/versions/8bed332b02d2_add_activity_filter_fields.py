"""add_activity_filter_fields

Revision ID: 8bed332b02d2
Revises: 3ce18b129b40
Create Date: 2025-12-01 19:24:12.058283

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bed332b02d2'
down_revision = '3ce18b129b40'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    location_type = sa.Enum('AT_HOME', 'IN_CLASS', 'OUTDOOR', 'ANY', name='locationtype')
    risk_level = sa.Enum('LOW', 'MEDIUM', 'HIGH', name='risklevel')
    skill_level = sa.Enum('BEGINNER', 'INTERMEDIATE', 'ADVANCED', name='skilllevel')
    
    location_type.create(op.get_bind(), checkfirst=True)
    risk_level.create(op.get_bind(), checkfirst=True)
    skill_level.create(op.get_bind(), checkfirst=True)
    
    # Add new columns to activities table
    op.add_column('activities', sa.Column('location', location_type, nullable=True))
    op.add_column('activities', sa.Column('risk_level', risk_level, nullable=True))
    op.add_column('activities', sa.Column('skill_level', skill_level, nullable=True))
    op.add_column('activities', sa.Column('theme', sa.ARRAY(sa.String()), nullable=True))


def downgrade() -> None:
    # Remove columns
    op.drop_column('activities', 'theme')
    op.drop_column('activities', 'skill_level')
    op.drop_column('activities', 'risk_level')
    op.drop_column('activities', 'location')
    
    # Drop enum types
    sa.Enum(name='skilllevel').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='risklevel').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='locationtype').drop(op.get_bind(), checkfirst=True)
