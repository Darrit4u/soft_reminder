from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.storage.base import Base, TimestampMixin, utc_now


def _uuid() -> str:
    return str(uuid4())


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    telegram_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(128), nullable=False, default="Europe/Berlin")
    locale: Mapped[str] = mapped_column(String(16), nullable=False, default="ru")
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    engagement_state: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    preferred_reminder_morning: Mapped[str | None] = mapped_column(String(5), nullable=True)
    preferred_reminder_day: Mapped[str | None] = mapped_column(String(5), nullable=True)
    preferred_reminder_evening: Mapped[str | None] = mapped_column(String(5), nullable=True)
    weekly_summary_day: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    weekly_summary_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    normalized_title: Mapped[str] = mapped_column(String(128), nullable=False)
    source: Mapped[str] = mapped_column(String(16), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    stage: Mapped[str] = mapped_column(String(16), nullable=False, default="adaptation")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class HabitCompletion(Base):
    __tablename__ = "habit_completions"
    __table_args__ = (UniqueConstraint("habit_id", "date", name="uq_habit_date"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    habit_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String(16), nullable=False)


class GratitudeEntry(Base):
    __tablename__ = "gratitude_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    items_count: Mapped[int] = mapped_column(Integer, nullable=False)
    parsed_items: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class WeeklyFeeling(Base):
    __tablename__ = "weekly_feelings"
    __table_args__ = (UniqueConstraint("user_id", "week_start_date", name="uq_user_week_feeling"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    week_start_date: Mapped[str] = mapped_column(String(10), nullable=False)
    week_end_date: Mapped[str] = mapped_column(String(10), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class UserSessionState(Base):
    __tablename__ = "user_session_states"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    state: Mapped[str] = mapped_column(String(64), nullable=False, default="idle")
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class WeeklySummaryLog(Base):
    __tablename__ = "weekly_summary_logs"
    __table_args__ = (UniqueConstraint("user_id", "week_start_date", name="uq_user_week_summary"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    week_start_date: Mapped[str] = mapped_column(String(10), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class DailyReminderLog(Base):
    __tablename__ = "daily_reminder_logs"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "date",
            "reminder_type",
            "window",
            name="uq_reminder_user_day_type_window",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    reminder_type: Mapped[str] = mapped_column(String(32), nullable=False)
    window: Mapped[str] = mapped_column(String(16), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
