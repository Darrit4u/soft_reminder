from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.config.constants import CALLBACK_PREFIXES
from src.storage.models import Habit


def default_habit_keyboard(default_habits: list[str], add_habit_label: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for idx, habit_name in enumerate(default_habits):
        rows.append(
            [
                InlineKeyboardButton(
                    text=habit_name,
                    callback_data=f"{CALLBACK_PREFIXES['ADD_HABIT_DEFAULT']}:{idx}",
                )
            ]
        )
    rows.append(
        [
                InlineKeyboardButton(
                    text=add_habit_label,
                    callback_data=CALLBACK_PREFIXES["ADD_HABIT_CUSTOM"],
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def pending_habits_keyboard(habits: list[Habit], date: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for habit in habits:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"✅ {habit.title}",
                    callback_data=f"{CALLBACK_PREFIXES['HABIT_DONE']}:{habit.id}:{date}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def weekly_habit_offer_keyboard(add_habit_label: str, keep_current_label: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=add_habit_label,
                    callback_data=CALLBACK_PREFIXES["ADD_HABIT_CUSTOM"],
                )
            ],
            [
                InlineKeyboardButton(
                    text=keep_current_label,
                    callback_data=CALLBACK_PREFIXES["KEEP_CURRENT_HABITS"],
                )
            ],
        ]
    )
