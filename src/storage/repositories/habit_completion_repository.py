from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.storage.models import HabitCompletion


class HabitCompletionRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def exists(self, habit_id: str, date: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(HabitCompletion.id).where(
                    and_(HabitCompletion.habit_id == habit_id, HabitCompletion.date == date)
                )
            )
            return result.scalar_one_or_none() is not None

    async def create_if_not_exists(
        self,
        user_id: str,
        habit_id: str,
        date: str,
        source: str,
    ) -> bool:
        async with self._session_factory() as session:
            entity = HabitCompletion(
                user_id=user_id,
                habit_id=habit_id,
                date=date,
                completed=True,
                completed_at=datetime.now(timezone.utc),
                source=source,
            )
            session.add(entity)
            try:
                await session.commit()
                return True
            except IntegrityError:
                await session.rollback()
                return False

    async def list_completed_habit_ids_for_day(self, user_id: str, date: str) -> list[str]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(HabitCompletion.habit_id).where(
                    and_(HabitCompletion.user_id == user_id, HabitCompletion.date == date, HabitCompletion.completed.is_(True))
                )
            )
            return [row[0] for row in result.all()]

    async def get_completion_dates_for_habit(
        self, user_id: str, habit_id: str, start_date: str, end_date: str
    ) -> list[str]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(HabitCompletion.date).where(
                    and_(
                        HabitCompletion.user_id == user_id,
                        HabitCompletion.habit_id == habit_id,
                        HabitCompletion.date >= start_date,
                        HabitCompletion.date <= end_date,
                        HabitCompletion.completed.is_(True),
                    )
                )
            )
            return [row[0] for row in result.all()]

    async def count_for_user_and_week(self, user_id: str, start_date: str, end_date: str) -> int:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.count(HabitCompletion.id)).where(
                    and_(
                        HabitCompletion.user_id == user_id,
                        HabitCompletion.date >= start_date,
                        HabitCompletion.date <= end_date,
                        HabitCompletion.completed.is_(True),
                    )
                )
            )
            return int(result.scalar_one() or 0)
