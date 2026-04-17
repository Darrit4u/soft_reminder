from __future__ import annotations

import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.app.types import AppServices
from src.config.env import Settings
from src.domain.engagement.service import EngagementService
from src.domain.feelings.service import FeelingsService
from src.domain.gratitude.service import GratitudeService
from src.domain.habits.service import HabitService
from src.domain.users.service import UserService
from src.domain.users.session_service import SessionService
from src.domain.weekly_summary.renderer import WeeklySummaryRenderer
from src.domain.weekly_summary.service import WeeklySummaryService
from src.jobs.daily_reminders import run_daily_reminders
from src.jobs.inactivity_check import run_inactivity_check
from src.jobs.weekly_summary import run_weekly_summaries
from src.messaging.message_engine import MessageEngine
from src.storage.db import create_engine, create_session_factory
from src.storage.init_db import create_all_tables
from src.storage.repositories.feelings_repository import FeelingsRepository
from src.storage.repositories.gratitude_repository import GratitudeRepository
from src.storage.repositories.habit_completion_repository import HabitCompletionRepository
from src.storage.repositories.habit_repository import HabitRepository
from src.storage.repositories.reminder_log_repository import ReminderLogRepository
from src.storage.repositories.session_repository import SessionRepository
from src.storage.repositories.user_repository import UserRepository
from src.storage.repositories.weekly_summary_log_repository import WeeklySummaryLogRepository
from src.telegram.callback_handlers import build_callback_router
from src.telegram.command_handlers import build_command_router
from src.telegram.text_handlers import build_text_router

logger = logging.getLogger(__name__)


def _build_message_engine() -> MessageEngine:
    path = Path("messages.json")
    engine = MessageEngine(path)
    required_paths = [
        "onboarding.welcome",
        "gratitude.responses.count_1_2",
        "habits.responses.completed_generic",
        "weekly_summary.header.mixed_week",
        "feelings_journal.response",
    ]
    missing = engine.validate_paths(required_paths)
    if missing:
        raise RuntimeError(f"Missing required message paths: {missing}")
    return engine


async def build_application(settings: Settings) -> tuple[Bot, Dispatcher, AppServices, AsyncIOScheduler]:
    db_engine = create_engine(settings.database_url)
    await create_all_tables(db_engine)
    session_factory = create_session_factory(db_engine)

    message_engine = _build_message_engine()
    user_repo = UserRepository(session_factory)
    session_repo = SessionRepository(session_factory)
    habit_repo = HabitRepository(session_factory)
    habit_completion_repo = HabitCompletionRepository(session_factory)
    gratitude_repo = GratitudeRepository(session_factory)
    feelings_repo = FeelingsRepository(session_factory)
    summary_log_repo = WeeklySummaryLogRepository(session_factory)
    reminder_log_repo = ReminderLogRepository(session_factory)

    user_service = UserService(
        user_repo=user_repo,
        default_timezone=settings.default_timezone,
        default_locale=settings.default_locale,
        weekly_summary_day=settings.weekly_summary_day,
        weekly_summary_time=settings.weekly_summary_time,
    )
    session_service = SessionService(session_repo)
    habit_service = HabitService(habit_repo, habit_completion_repo, user_repo, message_engine)
    gratitude_service = GratitudeService(gratitude_repo, user_repo, message_engine)
    feelings_service = FeelingsService(feelings_repo, user_repo, message_engine)
    engagement_service = EngagementService()
    weekly_renderer = WeeklySummaryRenderer(message_engine)
    weekly_summary_service = WeeklySummaryService(
        gratitude_service=gratitude_service,
        habit_service=habit_service,
        feelings_repo=feelings_repo,
        summary_log_repo=summary_log_repo,
        renderer=weekly_renderer,
    )

    services = AppServices(
        settings=settings,
        message_engine=message_engine,
        user_service=user_service,
        session_service=session_service,
        habit_service=habit_service,
        gratitude_service=gratitude_service,
        feelings_service=feelings_service,
        weekly_summary_service=weekly_summary_service,
        engagement_service=engagement_service,
        user_repo=user_repo,
        session_repo=session_repo,
        habit_repo=habit_repo,
        habit_completion_repo=habit_completion_repo,
        gratitude_repo=gratitude_repo,
        feelings_repo=feelings_repo,
        summary_log_repo=summary_log_repo,
        reminder_log_repo=reminder_log_repo,
    )

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dispatcher = Dispatcher()
    dispatcher.include_router(build_command_router(services))
    dispatcher.include_router(build_callback_router(services))
    dispatcher.include_router(build_text_router(services))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_daily_reminders, "interval", minutes=15, kwargs={"bot": bot, "services": services})
    scheduler.add_job(run_weekly_summaries, "interval", minutes=10, kwargs={"bot": bot, "services": services})
    scheduler.add_job(run_inactivity_check, "interval", hours=24, kwargs={"services": services})

    return bot, dispatcher, services, scheduler
