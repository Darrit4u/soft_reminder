from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.storage.models import UserSessionState


class SessionRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get(self, user_id: str) -> UserSessionState | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserSessionState).where(UserSessionState.user_id == user_id)
            )
            return result.scalar_one_or_none()

    async def set_state(self, user_id: str, state: str, payload: dict | None = None) -> None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserSessionState).where(UserSessionState.user_id == user_id)
            )
            entity = result.scalar_one_or_none()
            if entity is None:
                entity = UserSessionState(user_id=user_id, state=state, payload=payload)
                session.add(entity)
            else:
                entity.state = state
                entity.payload = payload
                entity.updated_at = datetime.now(timezone.utc)
            await session.commit()

    async def clear_state(self, user_id: str) -> None:
        await self.set_state(user_id, "idle", payload=None)
