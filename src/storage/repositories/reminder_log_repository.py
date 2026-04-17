from __future__ import annotations

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.storage.models import DailyReminderLog


class ReminderLogRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def count_for_day(self, user_id: str, date: str) -> int:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.count(DailyReminderLog.id)).where(
                    and_(DailyReminderLog.user_id == user_id, DailyReminderLog.date == date)
                )
            )
            return int(result.scalar_one() or 0)

    async def already_sent(
        self, user_id: str, date: str, reminder_type: str, window: str
    ) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(DailyReminderLog.id).where(
                    and_(
                        DailyReminderLog.user_id == user_id,
                        DailyReminderLog.date == date,
                        DailyReminderLog.reminder_type == reminder_type,
                        DailyReminderLog.window == window,
                    )
                )
            )
            return result.scalar_one_or_none() is not None

    async def mark_sent(self, user_id: str, date: str, reminder_type: str, window: str) -> bool:
        async with self._session_factory() as session:
            row = DailyReminderLog(
                user_id=user_id,
                date=date,
                reminder_type=reminder_type,
                window=window,
            )
            session.add(row)
            try:
                await session.commit()
                return True
            except IntegrityError:
                await session.rollback()
                return False
