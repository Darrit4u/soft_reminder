from __future__ import annotations

from src.messaging.message_engine import MessageEngine
from src.storage.models import User
from src.storage.repositories.feelings_repository import FeelingsRepository
from src.storage.repositories.user_repository import UserRepository
from src.utils.dates import get_week_range_for_user


class FeelingsService:
    def __init__(
        self,
        feelings_repo: FeelingsRepository,
        user_repo: UserRepository,
        message_engine: MessageEngine,
    ) -> None:
        self._feelings_repo = feelings_repo
        self._user_repo = user_repo
        self._message_engine = message_engine

    async def save_weekly_feeling(self, user: User, raw_text: str) -> str:
        week = get_week_range_for_user(user.timezone)
        await self._feelings_repo.upsert_for_week(
            user_id=user.id,
            week_start_date=week.start_date,
            week_end_date=week.end_date,
            raw_text=raw_text.strip(),
        )
        await self._user_repo.touch_activity(user.id)
        return self._message_engine.get_message("feelings_journal.response", user_id=user.id)

    async def get_recent_archive_text(self, user: User, limit: int = 4) -> str:
        entries = await self._feelings_repo.list_recent(user.id, limit=limit)
        if not entries:
            return self._message_engine.get_message(
                "feelings_journal.empty_archive", user_id=user.id
            )
        intro = self._message_engine.get_message("feelings_journal.archive_intro", user_id=user.id)
        lines = [intro]
        for idx, item in enumerate(entries, start=1):
            lines.append(
                f"{idx}. {item.week_start_date} - {item.week_end_date}: {item.raw_text}"
            )
        return "\n".join(lines)
