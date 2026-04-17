from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.app.types import AppServices
from src.config.constants import CALLBACK_PREFIXES, SESSION_STATES


def build_callback_router(services: AppServices) -> Router:
    router = Router(name="callbacks")

    async def _resolve_user(callback: CallbackQuery):
        tg_user = callback.from_user
        return await services.user_service.ensure_user(
            telegram_id=str(tg_user.id),
            username=tg_user.username,
            first_name=tg_user.first_name,
        )

    @router.callback_query(F.data.startswith(f"{CALLBACK_PREFIXES['ADD_HABIT_DEFAULT']}:"))
    async def add_default_habit_handler(callback: CallbackQuery) -> None:
        user = await _resolve_user(callback)
        defaults = services.message_engine.get_list("habits.defaults")
        _, idx_str = str(callback.data).split(":", maxsplit=1)
        try:
            idx = int(idx_str)
            habit_name = defaults[idx]
        except Exception:
            await callback.answer(
                services.message_engine.get_message("system.habits.add_failed", user_id=user.id),
                show_alert=True,
            )
            return

        _, warning = await services.habit_service.create_habit(
            user=user, title=habit_name, source="default"
        )
        if warning and callback.message:
            await callback.message.answer(warning)
        if callback.message:
            await callback.message.answer(
                services.message_engine.get_message(
                    "system.habits.added_default",
                    user_id=user.id,
                    placeholders={"habit_name": habit_name},
                )
            )
        await callback.answer(services.message_engine.get_message("system.callbacks.done", user_id=user.id))

    @router.callback_query(F.data == CALLBACK_PREFIXES["ADD_HABIT_CUSTOM"])
    async def add_custom_habit_handler(callback: CallbackQuery) -> None:
        user = await _resolve_user(callback)
        await services.session_service.set_state(
            user.id, SESSION_STATES["WAITING_FOR_CUSTOM_HABIT"]
        )
        if callback.message:
            await callback.message.answer(
                services.message_engine.get_message("system.habits.custom_prompt", user_id=user.id)
            )
        await callback.answer(
            services.message_engine.get_message("system.callbacks.wait_custom_habit", user_id=user.id)
        )

    @router.callback_query(F.data == CALLBACK_PREFIXES["KEEP_CURRENT_HABITS"])
    async def keep_current_handler(callback: CallbackQuery) -> None:
        user = await _resolve_user(callback)
        await callback.answer(
            services.message_engine.get_message("system.callbacks.keep_current", user_id=user.id)
        )
        if callback.message:
            await callback.message.answer(
                services.message_engine.get_message("system.habits.keep_current", user_id=user.id)
            )

    @router.callback_query(F.data.startswith(f"{CALLBACK_PREFIXES['HABIT_DONE']}:"))
    async def habit_done_handler(callback: CallbackQuery) -> None:
        user = await _resolve_user(callback)
        parts = str(callback.data).split(":")
        if len(parts) < 3:
            await callback.answer(
                services.message_engine.get_message("system.callbacks.bad_data", user_id=user.id),
                show_alert=True,
            )
            return
        habit_id = parts[1]
        text = await services.habit_service.complete_habit_for_today(
            user=user, habit_id=habit_id, source="button"
        )
        if callback.message:
            await callback.message.answer(text)
        await callback.answer(
            services.message_engine.get_message("system.callbacks.marked", user_id=user.id)
        )

    return router
