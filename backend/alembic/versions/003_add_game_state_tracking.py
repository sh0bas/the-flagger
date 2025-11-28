"""Add game state tracking fields

Revision ID: 003_add_game_state_tracking
Revises: 002_add_is_independent
Create Date: 2025-11-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_add_game_state_tracking'
down_revision: Union[str, None] = '002_add_is_independent'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add game state tracking columns
    op.add_column('game_sessions', sa.Column('country_ids', sa.ARRAY(sa.Integer()), nullable=False, server_default='{}'))
    op.add_column('game_sessions', sa.Column('current_question_index', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('game_sessions', sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('game_sessions', sa.Column('is_complete', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('game_sessions', sa.Column('answers', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'))


def downgrade() -> None:
    op.drop_column('game_sessions', 'answers')
    op.drop_column('game_sessions', 'is_complete')
    op.drop_column('game_sessions', 'current_streak')
    op.drop_column('game_sessions', 'current_question_index')
    op.drop_column('game_sessions', 'country_ids')
