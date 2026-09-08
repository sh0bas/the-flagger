"""Add entity_types and difficulties to game_sessions.

FlagQuizResult already accepted and the client already sent these filters,
but nothing persisted them - they were silently dropped on save. Persist
them the same way `regions` already is on this same table.

Revision ID: 006
Revises: 005
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'game_sessions',
        sa.Column('entity_types', sa.ARRAY(sa.String()), nullable=False, server_default='{}'),
    )
    op.add_column(
        'game_sessions',
        sa.Column('difficulties', sa.ARRAY(sa.String()), nullable=False, server_default='{}'),
    )


def downgrade() -> None:
    op.drop_column('game_sessions', 'difficulties')
    op.drop_column('game_sessions', 'entity_types')
