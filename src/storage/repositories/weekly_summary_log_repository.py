from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.storage.models import WeeklySummaryLog


class WeeklySummaryLogRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def exists(self, user_id: str, week_start_date: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(WeeklySummaryLog.id).where(
                    and_(
                        WeeklySummaryLog.user_id == user_id,
                        WeeklySummaryLog.week_start_date == week_start_date,
                    )
                )
            )
            return result.scalar_one_or_none() is not None

    async def mark_sent(self, user_id: str, week_start_date: str) -> bool:
        async with self._session_factory() as session:
            row = WeeklySummaryLog(user_id=user_id, week_start_date=week_start_date)
            session.add(row)
            try:
                await session.commit()
                return True
            except IntegrityError:
                await session.rollback()
                return False
