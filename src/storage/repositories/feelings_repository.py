from __future__ import annotations

from sqlalchemy import and_, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.storage.models import WeeklyFeeling


class FeelingsRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def upsert_for_week(
        self, user_id: str, week_start_date: str, week_end_date: str, raw_text: str
    ) -> WeeklyFeeling:
        async with self._session_factory() as session:
            entry = WeeklyFeeling(
                user_id=user_id,
                week_start_date=week_start_date,
                week_end_date=week_end_date,
                raw_text=raw_text,
            )
            session.add(entry)
            try:
                await session.commit()
                await session.refresh(entry)
                return entry
            except IntegrityError:
                await session.rollback()
                result = await session.execute(
                    select(WeeklyFeeling).where(
                        and_(
                            WeeklyFeeling.user_id == user_id,
                            WeeklyFeeling.week_start_date == week_start_date,
                        )
                    )
                )
                existing = result.scalar_one()
                existing.raw_text = raw_text
                existing.week_end_date = week_end_date
                await session.commit()
                await session.refresh(existing)
                return existing

    async def get_for_week(self, user_id: str, week_start_date: str) -> WeeklyFeeling | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(WeeklyFeeling).where(
                    and_(
                        WeeklyFeeling.user_id == user_id,
                        WeeklyFeeling.week_start_date == week_start_date,
                    )
                )
            )
            return result.scalar_one_or_none()

    async def list_recent(self, user_id: str, limit: int = 4) -> list[WeeklyFeeling]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(WeeklyFeeling)
                .where(WeeklyFeeling.user_id == user_id)
                .order_by(desc(WeeklyFeeling.week_start_date))
                .limit(limit)
            )
            return list(result.scalars().all())
