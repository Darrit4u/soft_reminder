from __future__ import annotations

from dataclasses import dataclass

from src.domain.gratitude.service import GratitudeService, WeeklyGratitudeStats
from src.domain.habits.service import HabitService, WeeklyHabitStats
from src.domain.weekly_summary.renderer import WeeklySummaryRenderer
from src.storage.models import User
from src.storage.repositories.feelings_repository import FeelingsRepository
from src.storage.repositories.weekly_summary_log_repository import WeeklySummaryLogRepository
from src.utils.dates import WeekRange, get_week_range_for_user


@dataclass(slots=True)
class WeeklySummaryContext:
    week: WeekRange
    gratitude: WeeklyGratitudeStats
    habits: WeeklyHabitStats
    feeling_text: str | None
    week_type: str


class WeeklySummaryService:
    def __init__(
        self,
        gratitude_service: GratitudeService,
        habit_service: HabitService,
        feelings_repo: FeelingsRepository,
        summary_log_repo: WeeklySummaryLogRepository,
        renderer: WeeklySummaryRenderer,
    ) -> None:
        self._gratitude_service = gratitude_service
        self._habit_service = habit_service
        self._feelings_repo = feelings_repo
        self._summary_log_repo = summary_log_repo
        self._renderer = renderer

    def classify_overall_week(
        self, gratitude_stats: WeeklyGratitudeStats, habit_stats: WeeklyHabitStats
    ) -> str:
        habit_completions = sum(item.completed_days for item in habit_stats.habits)
        if gratitude_stats.total_items == 0 and habit_completions == 0:
            return "empty_week"
        if habit_stats.strong_type == "strong" or (
            gratitude_stats.total_items >= 7
            and gratitude_stats.dynamic_type in {"growth", "stable"}
        ):
            return "strong_week"
        if habit_stats.strong_type == "weak" and gratitude_stats.total_items <= 2:
            return "weak_week"
        return "mixed_week"

    async def build_week_context(self, user: User, week: WeekRange | None = None) -> WeeklySummaryContext:
        target_week = week or get_week_range_for_user(user.timezone)
        gratitude = await self._gratitude_service.get_weekly_stats(
            user.id, target_week.start_date, target_week.end_date
        )
        habits = await self._habit_service.get_weekly_stats(
            user.id, target_week.start_date, target_week.end_date
        )
        feeling = await self._feelings_repo.get_for_week(user.id, target_week.start_date)
        week_type = self.classify_overall_week(gratitude, habits)
        return WeeklySummaryContext(
            week=target_week,
            gratitude=gratitude,
            habits=habits,
            feeling_text=feeling.raw_text if feeling else None,
            week_type=week_type,
        )

    async def render_summary(self, user: User, week: WeekRange | None = None) -> str:
        ctx = await self.build_week_context(user, week=week)
        return self._renderer.render(
            user_id=user.id,
            week_type=ctx.week_type,
            gratitude_stats=ctx.gratitude,
            habit_stats=ctx.habits,
            feeling_text=ctx.feeling_text,
        )

    async def send_if_due(self, user: User) -> tuple[bool, str | None]:
        week = get_week_range_for_user(user.timezone)
        already_sent = await self._summary_log_repo.exists(user.id, week.start_date)
        if already_sent:
            return False, None
        text = await self.render_summary(user, week=week)
        marked = await self._summary_log_repo.mark_sent(user.id, week.start_date)
        if not marked:
            return False, None
        return True, text
