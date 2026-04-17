from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from src.app.types import AppServices
from src.config.constants import SESSION_STATES
from src.telegram.keyboards import default_habit_keyboard, pending_habits_keyboard
from src.utils.dates import user_today_str


def build_command_router(services: AppServices) -> Router:
    router = Router(name="commands")

    async def _resolve_user(message: Message):
        from_user = message.from_user
        if from_user is None:
            return None
        return await services.user_service.ensure_user(
            telegram_id=str(from_user.id),
            username=from_user.username,
            first_name=from_user.first_name,
        )

    @router.message(CommandStart())
    async def start_handler(message: Message) -> None:
        user = await _resolve_user(message)
        if not user:
            return
        defaults = services.message_engine.get_list("habits.defaults")
        add_habit_label = services.message_engine.get_message("shared.buttons.add_habit", user_id=user.id)
        await message.answer(
            services.message_engine.get_message("onboarding.welcome", user_id=user.id)
        )
        await message.answer(
            services.message_engine.get_message("onboarding.product_explanation", user_id=user.id)
        )
        await message.answer(
            services.message_engine.get_message(
                "onboarding.habit_selection_intro", user_id=user.id
            ),
            reply_markup=default_habit_keyboard(defaults, add_habit_label=add_habit_label),
        )
        await message.answer(
            services.message_engine.get_message("onboarding.gratitude_intro", user_id=user.id)
        )
        await services.user_service.set_onboarding_completed(user.id, value=True)
        await services.session_service.set_idle(user.id)

    @router.message(Command("help"))
    async def help_handler(message: Message) -> None:
        user = await _resolve_user(message)
        if not user:
            return
        text = services.message_engine.get_message("system.help", user_id=user.id)
        await message.answer(text)

    @router.message(Command("gratitude"))
    async def gratitude_handler(message: Message) -> None:
        user = await _resolve_user(message)
        if not user:
            return
        await services.session_service.set_state(user.id, SESSION_STATES["WAITING_FOR_GRATITUDE"])
        hint = services.message_engine.get_message(
            "gratitude.rules_hint.input_format", user_id=user.id
        )
        soft_goal = services.message_engine.get_message(
            "gratitude.rules_hint.soft_goal", user_id=user.id
        )
        await message.answer(f"{hint}\n\n{soft_goal}")

    @router.message(Command("habits"))
    async def habits_handler(message: Message) -> None:
        user = await _resolve_user(message)
        if not user:
            return
        active = await services.habit_service.list_active_habits(user.id)
        if not active:
            defaults = services.message_engine.get_list("habits.defaults")
            add_habit_label = services.message_engine.get_message(
                "shared.buttons.add_habit", user_id=user.id
            )
            await message.answer(
                services.message_engine.get_message("system.habits.no_active_habits", user_id=user.id),
                reply_markup=default_habit_keyboard(defaults, add_habit_label=add_habit_label),
            )
            return
        pending = await services.habit_service.get_pending_habits_for_today(user)
        if not pending:
            await message.answer(
                services.message_engine.get_message("system.habits.all_done_today", user_id=user.id)
            )
            return
        prompt = services.message_engine.get_message(
            "habits.prompts.pending_habits", user_id=user.id
        )
        today = user_today_str(user.timezone)
        await message.answer(prompt, reply_markup=pending_habits_keyboard(pending, today))

    @router.message(Command("add_habit"))
    async def add_habit_handler(message: Message) -> None:
        user = await _resolve_user(message)
        if not user:
            return
        defaults = services.message_engine.get_list("habits.defaults")
        add_habit_label = services.message_engine.get_message("shared.buttons.add_habit", user_id=user.id)
        hint = services.message_engine.get_message(
            "habits.rules_hint.start_one_per_week", user_id=user.id
        )
        await message.answer(
            hint, reply_markup=default_habit_keyboard(defaults, add_habit_label=add_habit_label)
        )

    @router.message(Command("stats"))
    async def stats_handler(message: Message) -> None:
        user = await _resolve_user(message)
        if not user:
            return
        summary = await services.weekly_summary_service.render_summary(user)
        await message.answer(summary)
        prompt = services.message_engine.get_message("feelings_journal.prompt", user_id=user.id)
        await message.answer(prompt)
        await services.session_service.set_state(
            user.id, SESSION_STATES["WAITING_FOR_WEEKLY_FEELINGS"]
        )

    @router.message(Command("feelings"))
    async def feelings_handler(message: Message) -> None:
        user = await _resolve_user(message)
        if not user:
            return
        text = await services.feelings_service.get_recent_archive_text(user, limit=4)
        await message.answer(text)

    @router.message(Command("settings"))
    async def settings_handler(message: Message) -> None:
        user = await _resolve_user(message)
        if not user:
            return
        await message.answer(
            services.message_engine.get_message("system.settings.placeholder", user_id=user.id)
        )

    return router
