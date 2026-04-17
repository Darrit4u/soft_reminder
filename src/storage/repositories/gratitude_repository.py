from __future__ import annotations

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.storage.models import GratitudeEntry


class GratitudeRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(
        self, user_id: str, date: str, raw_text: str, items_count: int, parsed_items: list[str]
    ) -> GratitudeEntry:
        async with self._session_factory() as session:
            entry = GratitudeEntry(
                user_id=user_id,
                date=date,
                raw_text=raw_text,
                items_count=items_count,
                parsed_items=parsed_items,
            )
            session.add(entry)
            await session.commit()
            await session.refresh(entry)
            return entry

    async def has_entries_for_day(self, user_id: str, date: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(GratitudeEntry.id).where(
                    and_(GratitudeEntry.user_id == user_id, GratitudeEntry.date == date)
                )
            )
            return result.scalar_one_or_none() is not None

    async def sum_items_by_day(self, user_id: str, start_date: str, end_date: str) -> dict[str, int]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(GratitudeEntry.date, func.sum(GratitudeEntry.items_count))
                .where(
                    and_(
                        GratitudeEntry.user_id == user_id,
                        GratitudeEntry.date >= start_date,
                        GratitudeEntry.date <= end_date,
                    )
                )
                .group_by(GratitudeEntry.date)
            )
            return {str(day): int(total or 0) for day, total in result.all()}
