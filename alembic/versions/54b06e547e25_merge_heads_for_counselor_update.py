"""merge heads for counselor update

Revision ID: 54b06e547e25
Revises: 0a94e6e9533c, 0fd9a9c371bf
Create Date: 2025-11-28 20:14:07.812563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54b06e547e25'
down_revision = ('0a94e6e9533c', '0fd9a9c371bf')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
