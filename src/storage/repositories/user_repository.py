from __future__ import annotations

from datetime import datetime, timezone as dt_timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.storage.models import User


class UserRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_by_telegram_id(self, telegram_id: str) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()

    async def create(
        self,
        telegram_id: str,
        username: str | None,
        first_name: str | None,
        timezone: str,
        locale: str,
        weekly_summary_day: int,
        weekly_summary_time: str,
    ) -> User:
        async with self._session_factory() as session:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                timezone=timezone,
                locale=locale,
                weekly_summary_day=weekly_summary_day,
                weekly_summary_time=weekly_summary_time,
                last_activity_at=datetime.now(dt_timezone.utc),
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def set_onboarding_completed(self, user_id: str, value: bool = True) -> None:
        async with self._session_factory() as session:
            user = await session.get(User, user_id)
            if not user:
                return
            user.onboarding_completed = value
            user.updated_at = datetime.now(dt_timezone.utc)
            await session.commit()

    async def touch_activity(self, user_id: str) -> None:
        async with self._session_factory() as session:
            user = await session.get(User, user_id)
            if not user:
                return
            now = datetime.now(dt_timezone.utc)
            user.last_activity_at = now
            user.updated_at = now
            await session.commit()

    async def update_engagement_state(self, user_id: str, state: str) -> None:
        async with self._session_factory() as session:
            user = await session.get(User, user_id)
            if not user:
                return
            user.engagement_state = state
            user.updated_at = datetime.now(dt_timezone.utc)
            await session.commit()

    async def list_all(self) -> list[User]:
        async with self._session_factory() as session:
            result = await session.execute(select(User))
            return list(result.scalars().all())
