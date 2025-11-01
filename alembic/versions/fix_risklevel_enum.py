"""fix risklevel enum to include CRITICAL

Revision ID: fix_risklevel_enum
Revises: 099735097888
Create Date: 2025-10-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_risklevel_enum'
down_revision = '099735097888'
branch_labels = None
depends_on = None


def upgrade():
    # Add CRITICAL to the risklevel enum if it doesn't exist
    # PostgreSQL doesn't allow direct ALTER TYPE, so we need to use a workaround
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'CRITICAL' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'risklevel')
            ) THEN
                ALTER TYPE risklevel ADD VALUE 'CRITICAL';
            END IF;
        END $$;
    """)


def downgrade():
    # Note: PostgreSQL doesn't support removing enum values easily
    # This would require recreating the enum and all dependent columns
    pass
