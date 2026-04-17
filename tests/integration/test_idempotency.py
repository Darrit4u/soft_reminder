import asyncio
from pathlib import Path

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("aiosqlite")

from src.storage.base import Base
from src.storage.db import create_engine, create_session_factory
from src.storage.repositories.habit_completion_repository import HabitCompletionRepository
from src.storage.repositories.habit_repository import HabitRepository
from src.storage.repositories.reminder_log_repository import ReminderLogRepository
from src.storage.repositories.user_repository import UserRepository
from src.storage.repositories.weekly_summary_log_repository import WeeklySummaryLogRepository


def test_idempotency_constraints(tmp_path: Path) -> None:
    async def _run() -> None:
        db_path = tmp_path / "test.db"
        engine = create_engine(f"sqlite+aiosqlite:///{db_path}")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        sf = create_session_factory(engine)

        user_repo = UserRepository(sf)
        habit_repo = HabitRepository(sf)
        completion_repo = HabitCompletionRepository(sf)
        summary_repo = WeeklySummaryLogRepository(sf)
        reminder_repo = ReminderLogRepository(sf)

        user = await user_repo.create(
            telegram_id="123456",
            username="tester",
            first_name="Test",
            timezone="Europe/Berlin",
            locale="ru",
            weekly_summary_day=7,
            weekly_summary_time="19:00",
        )
        habit = await habit_repo.create(user.id, "Сделать короткую зарядку", "default")

        assert await completion_repo.create_if_not_exists(user.id, habit.id, "2026-04-18", "button")
        assert not await completion_repo.create_if_not_exists(user.id, habit.id, "2026-04-18", "text")

        assert await summary_repo.mark_sent(user.id, "2026-04-13")
        assert not await summary_repo.mark_sent(user.id, "2026-04-13")

        assert await reminder_repo.mark_sent(user.id, "2026-04-18", "gratitude", "morning")
        assert not await reminder_repo.mark_sent(user.id, "2026-04-18", "gratitude", "morning")
        assert await reminder_repo.already_sent(user.id, "2026-04-18", "gratitude", "morning")
        assert await reminder_repo.count_for_day(user.id, "2026-04-18") == 1

        await engine.dispose()

    asyncio.run(_run())
