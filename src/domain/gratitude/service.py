from __future__ import annotations

from dataclasses import dataclass

from src.config.constants import GRATITUDE
from src.domain.gratitude.parser import parse_gratitude_items
from src.messaging.message_engine import MessageEngine
from src.storage.models import User
from src.storage.repositories.gratitude_repository import GratitudeRepository
from src.storage.repositories.user_repository import UserRepository
from src.utils.dates import list_dates, user_today_str


@dataclass(slots=True)
class WeeklyGratitudeStats:
    total_items: int
    days_with_entries: int
    avg_per_day: float
    max_items_day: int
    first3_days_avg: float
    last3_days_avg: float
    dynamic_type: str  # growth|stable|irregular|low_data


class GratitudeService:
    def __init__(
        self,
        gratitude_repo: GratitudeRepository,
        user_repo: UserRepository,
        message_engine: MessageEngine,
    ) -> None:
        self._gratitude_repo = gratitude_repo
        self._user_repo = user_repo
        self._message_engine = message_engine

    def parse_items(self, text: str) -> list[str]:
        return parse_gratitude_items(text)

    async def handle_gratitude_text(self, user: User, text: str) -> str:
        items = self.parse_items(text)
        if len(items) == 0:
            return self._message_engine.get_message(
                "gratitude.responses.empty_followup", user_id=user.id
            )

        today = user_today_str(user.timezone)
        await self._gratitude_repo.create(
            user_id=user.id,
            date=today,
            raw_text=text,
            items_count=len(items),
            parsed_items=items,
        )
        await self._user_repo.touch_activity(user.id)

        if len(items) == 1 and "\n" not in text:
            key = "gratitude.responses.single_line_fallback"
        elif len(items) <= 2:
            key = "gratitude.responses.count_1_2"
        elif len(items) <= 5:
            key = "gratitude.responses.count_3_5"
        elif len(items) <= 9:
            key = "gratitude.responses.count_6_9"
        else:
            key = "gratitude.responses.count_10_plus"
        return self._message_engine.get_message(key, user_id=user.id)

    async def has_entry_today(self, user: User) -> bool:
        today = user_today_str(user.timezone)
        return await self._gratitude_repo.has_entries_for_day(user.id, today)

    async def get_weekly_stats(
        self, user_id: str, week_start: str, week_end: str
    ) -> WeeklyGratitudeStats:
        by_day = await self._gratitude_repo.sum_items_by_day(user_id, week_start, week_end)
        dates = list_dates(week_start, week_end)
        values = [int(by_day.get(day, 0)) for day in dates]

        total_items = sum(values)
        days_with_entries = sum(1 for v in values if v > 0)
        avg_per_day = total_items / 7.0
        max_items_day = max(values) if values else 0
        first3 = values[:3]
        last3 = values[-3:]
        first3_avg = sum(first3) / 3.0 if first3 else 0.0
        last3_avg = sum(last3) / 3.0 if last3 else 0.0

        if days_with_entries < 2 or total_items < 3:
            dynamic_type = "low_data"
        else:
            threshold = float(GRATITUDE["STABILITY_THRESHOLD"])
            diff = last3_avg - first3_avg
            if diff > threshold:
                dynamic_type = "growth"
            elif abs(diff) <= threshold:
                dynamic_type = "stable"
            else:
                dynamic_type = "irregular"

        return WeeklyGratitudeStats(
            total_items=total_items,
            days_with_entries=days_with_entries,
            avg_per_day=avg_per_day,
            max_items_day=max_items_day,
            first3_days_avg=first3_avg,
            last3_days_avg=last3_avg,
            dynamic_type=dynamic_type,
        )
