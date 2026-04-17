from __future__ import annotations

from datetime import datetime

from src.config.constants import ENGAGEMENT_THRESHOLDS
from src.utils.dates import inactive_days


class EngagementService:
    def get_engagement_state(
        self,
        last_activity_at: datetime | None,
        timezone: str,
        now: datetime | None = None,
    ) -> str:
        days = inactive_days(last_activity_at, tz_name=timezone, now=now)
        if days >= ENGAGEMENT_THRESHOLDS["INACTIVE_DAYS"]:
            return "inactive"
        if days >= ENGAGEMENT_THRESHOLDS["LOW_ACTIVITY_DAYS"]:
            return "low_activity"
        return "active"

    def gratitude_prompt_key_by_state(self, state: str, window: str) -> str:
        if state == "inactive":
            return "gratitude.prompts.inactive_return"
        if state == "low_activity":
            return "gratitude.prompts.low_activity"
        return f"gratitude.prompts.{window}"

    def habits_prompt_key_by_state(self, state: str) -> str:
        if state == "inactive":
            return "habits.prompts.inactive_return"
        if state == "low_activity":
            return "habits.prompts.low_activity"
        return "habits.prompts.daily_general"
