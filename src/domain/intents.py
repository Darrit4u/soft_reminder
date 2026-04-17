from __future__ import annotations

from src.config.constants import SESSION_STATES


def classify_text_intent(
    session_state: str,
    looks_gratitude: bool,
    has_habit_match: bool,
) -> str:
    if session_state == SESSION_STATES["WAITING_FOR_CUSTOM_HABIT"]:
        return "custom_habit_creation"
    if session_state == SESSION_STATES["WAITING_FOR_WEEKLY_FEELINGS"]:
        return "weekly_feelings"
    if session_state == SESSION_STATES["WAITING_FOR_GRATITUDE"]:
        return "gratitude_list"
    if looks_gratitude:
        return "gratitude_list"
    if has_habit_match:
        return "habit_completion"
    return "unknown"
