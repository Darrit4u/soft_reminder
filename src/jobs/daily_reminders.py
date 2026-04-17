from __future__ import annotations

import logging

from aiogram import Bot

from src.app.types import AppServices
from src.config.constants import REMINDERS
from src.telegram.keyboards import pending_habits_keyboard
from src.utils.dates import detect_window, user_now, user_today_str

logger = logging.getLogger(__name__)


async def run_daily_reminders(bot: Bot, services: AppServices) -> None:
    users = await services.user_service.list_users()
    for user in users:
        local_now = user_now(user.timezone)
        window = detect_window(local_now, REMINDERS["WINDOWS"])
        if not window:
            continue

        today = user_today_str(user.timezone, now=local_now)
        reminders_sent = await services.reminder_log_repo.count_for_day(user.id, today)
        if reminders_sent >= REMINDERS["MAX_PER_DAY"]:
            continue

        try:
            if not await services.gratitude_service.has_entry_today(user):
                already = await services.reminder_log_repo.already_sent(
                    user.id, today, "gratitude", window
                )
                if not already:
                    key = services.engagement_service.gratitude_prompt_key_by_state(
                        user.engagement_state, window
                    )
                    text = services.message_engine.get_message(key, user_id=user.id)
                    await bot.send_message(chat_id=int(user.telegram_id), text=text)
                    await services.reminder_log_repo.mark_sent(user.id, today, "gratitude", window)

            reminders_sent = await services.reminder_log_repo.count_for_day(user.id, today)
            if reminders_sent >= REMINDERS["MAX_PER_DAY"]:
                continue

            pending = await services.habit_service.get_pending_habits_for_today(user)
            if pending:
                already = await services.reminder_log_repo.already_sent(
                    user.id, today, "habits", window
                )
                if not already:
                    prompt_key = services.engagement_service.habits_prompt_key_by_state(
                        user.engagement_state
                    )
                    prompt = services.message_engine.get_message(prompt_key, user_id=user.id)
                    keyboard = pending_habits_keyboard(pending, today)
                    await bot.send_message(
                        chat_id=int(user.telegram_id), text=prompt, reply_markup=keyboard
                    )
                    await services.reminder_log_repo.mark_sent(user.id, today, "habits", window)
        except Exception:
            logger.exception("daily reminder failed for user_id=%s", user.id)
