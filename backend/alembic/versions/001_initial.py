"""Initial database schema

Revision ID: 001_initial
Revises: 
Create Date: 2025-11-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table

    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=50), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'])
    op.create_index(op.f('ix_users_email'), 'users', ['email'])
    
    # Create countries table
    op.create_table(
        'countries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('capital', sa.String(length=100), nullable=False),
        sa.Column('region', postgresql.ENUM('americas', 'europe', 'africa', 'asia', 'oceania', name='regionenum'), nullable=False),
        sa.Column('flag_url', sa.String(length=500), nullable=False),
        sa.Column('iso_code', sa.String(length=2), nullable=False),
        sa.Column('alt_names', postgresql.ARRAY(sa.String()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('iso_code')
    )
    op.create_index(op.f('ix_countries_name'), 'countries', ['name'])
    op.create_index(op.f('ix_countries_region'), 'countries', ['region'])
    
    # Create game_sessions table
    op.create_table(
        'game_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_mode', postgresql.ENUM('flag_to_country', 'country_to_capital', 'capital_to_country', name='gamemodeenum'), nullable=False),
        sa.Column('regions', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('questions_count', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('correct_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_response_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('played_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_game_sessions_user_id'), 'game_sessions', ['user_id'])
    op.create_index(op.f('ix_game_sessions_game_mode'), 'game_sessions', ['game_mode'])
    op.create_index(op.f('ix_game_sessions_played_at'), 'game_sessions', ['played_at'])
    
    # Create friendships table
    op.create_table(
        'friendships',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requester_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('addressee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'accepted', 'declined', name='friendshipstatus'), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['addressee_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('requester_id', 'addressee_id', name='unique_friendship')
    )
    op.create_index(op.f('ix_friendships_status'), 'friendships', ['status'])
    
    # Create blocks table
    op.create_table(
        'blocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('blocker_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('blocked_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['blocker_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['blocked_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('blocker_id', 'blocked_id', name='unique_block')
    )


def downgrade() -> None:
    op.drop_table('blocks')
    op.drop_table('friendships')
    op.drop_table('game_sessions')
    op.drop_table('countries')
    op.drop_table('users')
    op.execute('DROP TYPE gamemodeenum')
    op.execute('DROP TYPE friendshipstatus')
    op.execute('DROP TYPE regionenum')
