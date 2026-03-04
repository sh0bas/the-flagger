"""Add difficulty and entity_type to countries

Revision ID: 004_add_difficulty_and_entity_type
Revises: 003_add_game_state_tracking
Create Date: 2025-11-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003_add_game_state_tracking'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE difficultyenum AS ENUM ('easy', 'medium', 'hard')")
    op.execute("CREATE TYPE entitytypeenum AS ENUM ('sovereign_state', 'territory', 'us_state')")

    # Add difficulty column
    op.add_column('countries', sa.Column(
        'difficulty',
        sa.Enum('easy', 'medium', 'hard', name='difficultyenum'),
        nullable=False,
        server_default='medium'
    ))

    # Add entity_type column
    op.add_column('countries', sa.Column(
        'entity_type',
        sa.Enum('sovereign_state', 'territory', 'us_state', name='entitytypeenum'),
        nullable=False,
        server_default='sovereign_state'
    ))

    # Backfill: non-independent countries become territories
    op.execute("UPDATE countries SET entity_type = 'territory' WHERE is_independent = false")

    # Widen iso_code to accept longer codes (e.g. 'us-ca' for future US states)
    op.alter_column('countries', 'iso_code', type_=sa.String(10))


def downgrade() -> None:
    op.drop_column('countries', 'entity_type')
    op.drop_column('countries', 'difficulty')
    op.execute("DROP TYPE IF EXISTS entitytypeenum")
    op.execute("DROP TYPE IF EXISTS difficultyenum")
    op.alter_column('countries', 'iso_code', type_=sa.String(2))
