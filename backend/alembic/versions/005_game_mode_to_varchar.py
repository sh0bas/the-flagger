"""Convert game_sessions.game_mode from an enum type to varchar.

The gamemodeenum type was created in 001 with three values. The application
later added practice/endless/gauntlet without a migration, so every write from
the only game endpoint the frontend calls failed at INSERT.

Rather than keep adding values to a Postgres type, mode is now plain text and
the allowed set is enforced by the Pydantic schema — at the trust boundary,
where the check actually belongs. The USING cast preserves all existing rows.

Revision ID: 005
Revises: 004
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'game_sessions',
        'game_mode',
        existing_type=sa.Enum(name='gamemodeenum'),
        type_=sa.String(length=20),
        existing_nullable=False,
        postgresql_using='game_mode::text',
    )
    op.execute('DROP TYPE gamemodeenum')


def downgrade() -> None:
    # Rows using practice/endless/gauntlet can't be represented by the old
    # enum. Refuse rather than silently deleting real game history — by the
    # time this migration has been live for any length of time, that's every
    # row, since nothing writes the old values anymore.
    conn = op.get_bind()
    incompatible = conn.execute(
        sa.text(
            "SELECT count(*) FROM game_sessions WHERE game_mode NOT IN "
            "('flag_to_country', 'country_to_capital', 'capital_to_country')"
        )
    ).scalar()
    if incompatible:
        raise RuntimeError(
            f"Refusing to downgrade: {incompatible} game_sessions row(s) use a "
            "game_mode value ('practice'/'endless'/'gauntlet') the old "
            "gamemodeenum can't represent. Back up and manually clear or "
            "migrate these rows first if you really want to downgrade."
        )
    op.execute(
        "CREATE TYPE gamemodeenum AS ENUM "
        "('flag_to_country', 'country_to_capital', 'capital_to_country')"
    )
    op.alter_column(
        'game_sessions',
        'game_mode',
        existing_type=sa.String(length=20),
        type_=sa.Enum(name='gamemodeenum'),
        existing_nullable=False,
        postgresql_using='game_mode::gamemodeenum',
    )
