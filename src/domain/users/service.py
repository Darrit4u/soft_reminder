from __future__ import annotations

from src.storage.models import User
from src.storage.repositories.user_repository import UserRepository


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        default_timezone: str,
        default_locale: str,
        weekly_summary_day: int,
        weekly_summary_time: str,
    ) -> None:
        self._user_repo = user_repo
        self._default_timezone = default_timezone
        self._default_locale = default_locale
        self._weekly_summary_day = weekly_summary_day
        self._weekly_summary_time = weekly_summary_time

    async def ensure_user(
        self, telegram_id: str, username: str | None = None, first_name: str | None = None
    ) -> User:
        existing = await self._user_repo.get_by_telegram_id(telegram_id)
        if existing:
            return existing
        return await self._user_repo.create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            timezone=self._default_timezone,
            locale=self._default_locale,
            weekly_summary_day=self._weekly_summary_day,
            weekly_summary_time=self._weekly_summary_time,
        )

    async def touch_activity(self, user_id: str) -> None:
        await self._user_repo.touch_activity(user_id)

    async def set_onboarding_completed(self, user_id: str, value: bool = True) -> None:
        await self._user_repo.set_onboarding_completed(user_id, value)

    async def get_by_id(self, user_id: str) -> User | None:
        return await self._user_repo.get_by_id(user_id)

    async def list_users(self) -> list[User]:
        return await self._user_repo.list_all()

    async def update_engagement_state(self, user_id: str, state: str) -> None:
        await self._user_repo.update_engagement_state(user_id, state)
