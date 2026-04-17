from __future__ import annotations

from src.config.constants import SESSION_STATES
from src.storage.models import UserSessionState
from src.storage.repositories.session_repository import SessionRepository


class SessionService:
    def __init__(self, repo: SessionRepository) -> None:
        self._repo = repo

    async def get_state(self, user_id: str) -> UserSessionState | None:
        return await self._repo.get(user_id)

    async def set_state(self, user_id: str, state: str, payload: dict | None = None) -> None:
        await self._repo.set_state(user_id, state, payload)

    async def clear_state(self, user_id: str) -> None:
        await self._repo.clear_state(user_id)

    async def set_idle(self, user_id: str) -> None:
        await self._repo.set_state(user_id, SESSION_STATES["IDLE"])
