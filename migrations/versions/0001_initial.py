"""Initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-18
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("telegram_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=128), nullable=False, server_default="Europe/Berlin"),
        sa.Column("locale", sa.String(length=16), nullable=False, server_default="ru"),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("engagement_state", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("preferred_reminder_morning", sa.String(length=5), nullable=True),
        sa.Column("preferred_reminder_day", sa.String(length=5), nullable=True),
        sa.Column("preferred_reminder_evening", sa.String(length=5), nullable=True),
        sa.Column("weekly_summary_day", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("weekly_summary_time", sa.String(length=5), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])

    op.create_table(
        "habits",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("normalized_title", sa.String(length=128), nullable=False),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("stage", sa.String(length=16), nullable=False, server_default="adaptation"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_habits_user_id", "habits", ["user_id"])

    op.create_table(
        "habit_completions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("habit_id", sa.String(length=36), sa.ForeignKey("habits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.String(length=10), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.UniqueConstraint("habit_id", "date", name="uq_habit_date"),
    )
    op.create_index("ix_habit_completions_user_id", "habit_completions", ["user_id"])
    op.create_index("ix_habit_completions_habit_id", "habit_completions", ["habit_id"])
    op.create_index("ix_habit_completions_date", "habit_completions", ["date"])

    op.create_table(
        "gratitude_entries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.String(length=10), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("items_count", sa.Integer(), nullable=False),
        sa.Column("parsed_items", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_gratitude_entries_user_id", "gratitude_entries", ["user_id"])
    op.create_index("ix_gratitude_entries_date", "gratitude_entries", ["date"])

    op.create_table(
        "weekly_feelings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("week_start_date", sa.String(length=10), nullable=False),
        sa.Column("week_end_date", sa.String(length=10), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "week_start_date", name="uq_user_week_feeling"),
    )
    op.create_index("ix_weekly_feelings_user_id", "weekly_feelings", ["user_id"])

    op.create_table(
        "user_session_states",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("state", sa.String(length=64), nullable=False, server_default="idle"),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "weekly_summary_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("week_start_date", sa.String(length=10), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "week_start_date", name="uq_user_week_summary"),
    )
    op.create_index("ix_weekly_summary_logs_user_id", "weekly_summary_logs", ["user_id"])

    op.create_table(
        "daily_reminder_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.String(length=10), nullable=False),
        sa.Column("reminder_type", sa.String(length=32), nullable=False),
        sa.Column("window", sa.String(length=16), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "user_id",
            "date",
            "reminder_type",
            "window",
            name="uq_reminder_user_day_type_window",
        ),
    )
    op.create_index("ix_daily_reminder_logs_user_id", "daily_reminder_logs", ["user_id"])
    op.create_index("ix_daily_reminder_logs_date", "daily_reminder_logs", ["date"])


def downgrade() -> None:
    op.drop_index("ix_daily_reminder_logs_date", table_name="daily_reminder_logs")
    op.drop_index("ix_daily_reminder_logs_user_id", table_name="daily_reminder_logs")
    op.drop_table("daily_reminder_logs")

    op.drop_index("ix_weekly_summary_logs_user_id", table_name="weekly_summary_logs")
    op.drop_table("weekly_summary_logs")

    op.drop_table("user_session_states")

    op.drop_index("ix_weekly_feelings_user_id", table_name="weekly_feelings")
    op.drop_table("weekly_feelings")

    op.drop_index("ix_gratitude_entries_date", table_name="gratitude_entries")
    op.drop_index("ix_gratitude_entries_user_id", table_name="gratitude_entries")
    op.drop_table("gratitude_entries")

    op.drop_index("ix_habit_completions_date", table_name="habit_completions")
    op.drop_index("ix_habit_completions_habit_id", table_name="habit_completions")
    op.drop_index("ix_habit_completions_user_id", table_name="habit_completions")
    op.drop_table("habit_completions")

    op.drop_index("ix_habits_user_id", table_name="habits")
    op.drop_table("habits")

    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
