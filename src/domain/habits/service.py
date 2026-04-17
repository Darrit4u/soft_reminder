from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from src.messaging.message_engine import MessageEngine
from src.storage.models import Habit, User
from src.storage.repositories.habit_completion_repository import HabitCompletionRepository
from src.storage.repositories.habit_repository import HabitRepository
from src.storage.repositories.user_repository import UserRepository
from src.utils.dates import list_dates, user_today_str
from src.utils.text import is_probably_emoji_only
from .parser import detect_habit_completion

_ABSTRACT_BLOCKLIST = {"быть лучше", "жить нормально", "стать продуктивным"}


@dataclass(slots=True)
class HabitWeeklyItemStats:
    habit_id: str
    habit_name: str
    completed_days: int
    total_days: int
    completion_rate: int
    current_streak: int
    best_streak: int
    stage: str


@dataclass(slots=True)
class WeeklyHabitStats:
    habits: list[HabitWeeklyItemStats]
    strong_type: str
    most_consistent_habit_name: str | None
    has_adaptation_habits: bool


class HabitService:
    def __init__(
        self,
        habit_repo: HabitRepository,
        completion_repo: HabitCompletionRepository,
        user_repo: UserRepository,
        message_engine: MessageEngine,
    ) -> None:
        self._habit_repo = habit_repo
        self._completion_repo = completion_repo
        self._user_repo = user_repo
        self._message_engine = message_engine

    def _msg(self, user_id: str, path: str) -> str:
        return self._message_engine.get_message(path, user_id=user_id)

    async def list_active_habits(self, user_id: str) -> list[Habit]:
        return await self._habit_repo.get_active_by_user(user_id)

    def validate_custom_habit(self, user_id: str, text: str) -> tuple[bool, str | None]:
        title = text.strip()
        if len(title) < 2:
            return False, self._msg(user_id, "system.validation.habit_too_short")
        if len(title) > 80:
            return False, self._msg(user_id, "system.validation.habit_too_long")
        if is_probably_emoji_only(title):
            return False, self._msg(user_id, "system.validation.habit_emoji_only")
        if title.lower() in _ABSTRACT_BLOCKLIST:
            return False, self._msg(user_id, "system.validation.habit_too_abstract")
        return True, None

    async def create_habit(self, user: User, title: str, source: str) -> tuple[Habit, str | None]:
        warning: str | None = None
        if source == "custom":
            local_today = datetime.now(ZoneInfo(user.timezone)).date()
            today = local_today
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            local_tz = ZoneInfo(user.timezone)
            week_start_local = datetime.combine(monday, time.min, tzinfo=local_tz)
            week_end_local = datetime.combine(sunday, time.max, tzinfo=local_tz)
            week_start_dt = week_start_local.astimezone(timezone.utc)
            week_end_dt = week_end_local.astimezone(timezone.utc)
            weekly_count = await self._habit_repo.count_created_between(
                user.id, week_start_dt, week_end_dt
            )
            if weekly_count >= 1:
                warning = self._message_engine.get_message(
                    "habits.responses.multiple_habits_warning", user_id=user.id
                )
        habit = await self._habit_repo.create(user_id=user.id, title=title, source=source)
        await self._user_repo.touch_activity(user.id)
        return habit, warning

    async def get_pending_habits_for_today(self, user: User) -> list[Habit]:
        active = await self.list_active_habits(user.id)
        today = user_today_str(user.timezone)
        completed_ids = set(
            await self._completion_repo.list_completed_habit_ids_for_day(user.id, today)
        )
        return [h for h in active if h.id not in completed_ids]

    async def complete_habit_for_today(self, user: User, habit_id: str, source: str) -> str:
        habit = await self._habit_repo.get_by_id_for_user(user.id, habit_id)
        if not habit:
            return self._msg(user.id, "system.habits.not_found")

        today = user_today_str(user.timezone)
        created = await self._completion_repo.create_if_not_exists(
            user_id=user.id, habit_id=habit_id, date=today, source=source
        )
        if not created:
            return self._msg(user.id, "system.habits.already_done")

        await self._user_repo.touch_activity(user.id)
        active = await self.list_active_habits(user.id)
        completed_today = await self._completion_repo.list_completed_habit_ids_for_day(user.id, today)
        pending_count = len([h for h in active if h.id not in set(completed_today)])

        key = "habits.responses.completed_generic"
        if len(completed_today) == 1:
            key = "habits.responses.completed_first_today"
        if pending_count == 0 and len(active) > 0:
            key = "habits.responses.completed_last_today"
        return self._message_engine.get_message(key, user_id=user.id)

    async def detect_completion_from_text(self, user_id: str, text: str) -> Habit | None:
        active = await self.list_active_habits(user_id)
        return detect_habit_completion(text, active)

    def _streaks_for_week(self, completion_dates: set[str], week_dates: list[str]) -> tuple[int, int]:
        best = 0
        current = 0
        running = 0
        for day in week_dates:
            if day in completion_dates:
                running += 1
                best = max(best, running)
            else:
                running = 0
        for day in reversed(week_dates):
            if day in completion_dates:
                current += 1
            else:
                break
        return current, best

    async def get_weekly_stats(self, user_id: str, week_start: str, week_end: str) -> WeeklyHabitStats:
        habits = await self.list_active_habits(user_id)
        if not habits:
            return WeeklyHabitStats(
                habits=[],
                strong_type="empty",
                most_consistent_habit_name=None,
                has_adaptation_habits=False,
            )

        week_days = list_dates(week_start, week_end)
        items: list[HabitWeeklyItemStats] = []
        rates: list[int] = []

        for habit in habits:
            completion_dates = set(
                await self._completion_repo.get_completion_dates_for_habit(
                    user_id=user_id, habit_id=habit.id, start_date=week_start, end_date=week_end
                )
            )
            completed_days = len(completion_dates)
            total_days = len(week_days)
            rate = round((completed_days / total_days) * 100) if total_days > 0 else 0
            current_streak, best_streak = self._streaks_for_week(completion_dates, week_days)
            items.append(
                HabitWeeklyItemStats(
                    habit_id=habit.id,
                    habit_name=habit.title,
                    completed_days=completed_days,
                    total_days=total_days,
                    completion_rate=rate,
                    current_streak=current_streak,
                    best_streak=best_streak,
                    stage=habit.stage,
                )
            )
            rates.append(rate)

        avg_rate = sum(rates) / len(rates) if rates else 0.0
        if avg_rate >= 70:
            strong_type = "strong"
        elif avg_rate >= 35:
            strong_type = "mixed"
        else:
            strong_type = "weak"

        most_consistent = max(items, key=lambda item: item.completion_rate, default=None)
        has_adaptation = any(item.stage == "adaptation" for item in items)
        return WeeklyHabitStats(
            habits=items,
            strong_type=strong_type,
            most_consistent_habit_name=most_consistent.habit_name if most_consistent else None,
            has_adaptation_habits=has_adaptation,
        )
