"""Add is_independent field to countries

Revision ID: 002_add_is_independent
Revises: 001_initial
Create Date: 2025-11-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_add_is_independent'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_independent column
    op.add_column('countries', sa.Column('is_independent', sa.Boolean(), nullable=False, server_default='true'))
    # Create index on is_independent for faster filtering
    op.create_index(op.f('ix_countries_is_independent'), 'countries', ['is_independent'])


def downgrade() -> None:
    op.drop_index(op.f('ix_countries_is_independent'), table_name='countries')
    op.drop_column('countries', 'is_independent')
