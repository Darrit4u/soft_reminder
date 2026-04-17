from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.storage.models import Habit
from src.utils.text import normalize_text


class HabitRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, user_id: str, title: str, source: str) -> Habit:
        async with self._session_factory() as session:
            habit = Habit(
                user_id=user_id,
                title=title.strip(),
                normalized_title=normalize_text(title),
                source=source,
            )
            session.add(habit)
            await session.commit()
            await session.refresh(habit)
            return habit

    async def get_active_by_user(self, user_id: str) -> list[Habit]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Habit).where(and_(Habit.user_id == user_id, Habit.active.is_(True)))
            )
            habits = list(result.scalars().all())
            now = datetime.now(timezone.utc)
            changed = False
            for habit in habits:
                if habit.stage == "adaptation" and (now - habit.created_at).days >= 7:
                    habit.stage = "stable"
                    changed = True
            if changed:
                await session.commit()
            return habits

    async def get_by_id_for_user(self, user_id: str, habit_id: str) -> Habit | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Habit).where(
                    and_(Habit.user_id == user_id, Habit.id == habit_id, Habit.active.is_(True))
                )
            )
            return result.scalar_one_or_none()

    async def count_created_between(self, user_id: str, start_dt: datetime, end_dt: datetime) -> int:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.count(Habit.id)).where(
                    and_(Habit.user_id == user_id, Habit.created_at >= start_dt, Habit.created_at <= end_dt)
                )
            )
            return int(result.scalar_one() or 0)
