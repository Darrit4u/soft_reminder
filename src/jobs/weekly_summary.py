from __future__ import annotations

import logging

from aiogram import Bot

from src.app.types import AppServices
from src.config.constants import SESSION_STATES
from src.utils.dates import user_now

logger = logging.getLogger(__name__)


def _is_due(local_now, target_day: int, target_time: str, tolerance_minutes: int = 14) -> bool:
    if local_now.isoweekday() != target_day:
        return False
    try:
        hour_s, minute_s = target_time.split(":", maxsplit=1)
        target_minutes = int(hour_s) * 60 + int(minute_s)
    except ValueError:
        return False
    now_minutes = local_now.hour * 60 + local_now.minute
    return abs(now_minutes - target_minutes) <= tolerance_minutes


async def run_weekly_summaries(bot: Bot, services: AppServices) -> None:
    users = await services.user_service.list_users()
    for user in users:
        local_now = user_now(user.timezone)
        target_day = user.weekly_summary_day or services.settings.weekly_summary_day
        target_time = user.weekly_summary_time or services.settings.weekly_summary_time
        if not _is_due(local_now, target_day, target_time):
            continue

        try:
            sent, text = await services.weekly_summary_service.send_if_due(user)
            if not sent or not text:
                continue
            await bot.send_message(chat_id=int(user.telegram_id), text=text)
            prompt = services.message_engine.get_message("feelings_journal.prompt", user_id=user.id)
            await bot.send_message(chat_id=int(user.telegram_id), text=prompt)
            await services.session_service.set_state(
                user.id, SESSION_STATES["WAITING_FOR_WEEKLY_FEELINGS"]
            )
        except Exception:
            logger.exception("weekly summary failed for user_id=%s", user.id)
