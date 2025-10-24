"""change_processed_column_to_boolean

Revision ID: 9f678d9ee3dc
Revises: a0e01f23e14c
Create Date: 2025-10-24 13:13:40.981042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f678d9ee3dc'
down_revision = 'a0e01f23e14c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add processed column as BOOLEAN to observations table if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='observations' AND column_name='processed') THEN
                ALTER TABLE observations ADD COLUMN processed BOOLEAN NOT NULL DEFAULT FALSE;
            ELSE
                ALTER TABLE observations ALTER COLUMN processed TYPE BOOLEAN USING processed::boolean;
            END IF;
        END $$;
    """)
    
    # Add processed column as BOOLEAN to cases table if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='cases' AND column_name='processed') THEN
                ALTER TABLE cases ADD COLUMN processed BOOLEAN NOT NULL DEFAULT FALSE;
            ELSE
                ALTER TABLE cases ALTER COLUMN processed TYPE BOOLEAN USING processed::boolean;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Drop processed column from observations table
    op.drop_column('observations', 'processed')
    
    # Drop processed column from cases table
    op.drop_column('cases', 'processed')
