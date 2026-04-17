from __future__ import annotations

import random

from aiogram import Router
from aiogram.types import Message

from src.app.types import AppServices
from src.config.constants import SESSION_STATES
from src.domain.gratitude.parser import looks_like_gratitude_list
from src.domain.intents import classify_text_intent


def build_text_router(services: AppServices) -> Router:
    router = Router(name="text")

    @router.message()
    async def incoming_text_handler(message: Message) -> None:
        if not message.text or not message.from_user:
            return
        user = await services.user_service.ensure_user(
            telegram_id=str(message.from_user.id),
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )
        session = await services.session_service.get_state(user.id)
        state = session.state if session else SESSION_STATES["IDLE"]
        looks_gratitude = looks_like_gratitude_list(
            message.text, waiting_for_gratitude=state == SESSION_STATES["WAITING_FOR_GRATITUDE"]
        )
        matched_habit = None
        if not looks_gratitude and state == SESSION_STATES["IDLE"]:
            matched_habit = await services.habit_service.detect_completion_from_text(
                user.id, message.text
            )
        intent = classify_text_intent(
            session_state=state,
            looks_gratitude=looks_gratitude,
            has_habit_match=matched_habit is not None,
        )

        if intent == "custom_habit_creation":
            is_valid, validation_error = services.habit_service.validate_custom_habit(
                user.id, message.text
            )
            if not is_valid:
                await message.answer(
                    validation_error
                    or services.message_engine.get_message(
                        "system.validation.generic_error", user_id=user.id
                    )
                )
                return
            _, warning = await services.habit_service.create_habit(
                user=user, title=message.text, source="custom"
            )
            if warning:
                await message.answer(warning)
            await message.answer(
                services.message_engine.get_message(
                    "habits.responses.custom_habit_added", user_id=user.id
                )
            )
            await services.session_service.set_idle(user.id)
            return

        if intent == "weekly_feelings":
            response = await services.feelings_service.save_weekly_feeling(user, message.text)
            await message.answer(response)
            await services.session_service.set_idle(user.id)
            return

        if intent == "gratitude_list":
            response = await services.gratitude_service.handle_gratitude_text(user, message.text)
            await message.answer(response)
            if state == SESSION_STATES["WAITING_FOR_GRATITUDE"]:
                await services.session_service.set_idle(user.id)
            return

        if intent == "habit_completion" and matched_habit:
            response = await services.habit_service.complete_habit_for_today(
                user=user, habit_id=matched_habit.id, source="text"
            )
            await message.answer(response)
            return

        unknown = services.message_engine.get_list("system.unknown")
        await message.answer(random.choice(unknown))

    return router
