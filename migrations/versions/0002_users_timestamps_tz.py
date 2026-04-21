"""Make users created_at/updated_at timezone-aware

Revision ID: 0002_users_timestamps_tz
Revises: 0001_initial
Create Date: 2026-04-18
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_users_timestamps_tz"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING created_at AT TIME ZONE 'UTC'
        """
    )
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING updated_at AT TIME ZONE 'UTC'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
        USING created_at AT TIME ZONE 'UTC'
        """
    )
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
        USING updated_at AT TIME ZONE 'UTC'
        """
    )
