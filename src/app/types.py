from __future__ import annotations

from dataclasses import dataclass

from src.config.env import Settings
from src.domain.engagement.service import EngagementService
from src.domain.feelings.service import FeelingsService
from src.domain.gratitude.service import GratitudeService
from src.domain.habits.service import HabitService
from src.domain.users.service import UserService
from src.domain.users.session_service import SessionService
from src.domain.weekly_summary.service import WeeklySummaryService
from src.messaging.message_engine import MessageEngine
from src.storage.repositories.feelings_repository import FeelingsRepository
from src.storage.repositories.gratitude_repository import GratitudeRepository
from src.storage.repositories.habit_completion_repository import HabitCompletionRepository
from src.storage.repositories.habit_repository import HabitRepository
from src.storage.repositories.reminder_log_repository import ReminderLogRepository
from src.storage.repositories.session_repository import SessionRepository
from src.storage.repositories.user_repository import UserRepository
from src.storage.repositories.weekly_summary_log_repository import WeeklySummaryLogRepository


@dataclass(slots=True)
class AppServices:
    settings: Settings
    message_engine: MessageEngine
    user_service: UserService
    session_service: SessionService
    habit_service: HabitService
    gratitude_service: GratitudeService
    feelings_service: FeelingsService
    weekly_summary_service: WeeklySummaryService
    engagement_service: EngagementService
    user_repo: UserRepository
    session_repo: SessionRepository
    habit_repo: HabitRepository
    habit_completion_repo: HabitCompletionRepository
    gratitude_repo: GratitudeRepository
    feelings_repo: FeelingsRepository
    summary_log_repo: WeeklySummaryLogRepository
    reminder_log_repo: ReminderLogRepository
