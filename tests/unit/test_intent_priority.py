from src.config.constants import SESSION_STATES
from src.domain.intents import classify_text_intent


def test_session_state_has_priority() -> None:
    intent = classify_text_intent(
        session_state=SESSION_STATES["WAITING_FOR_CUSTOM_HABIT"],
        looks_gratitude=True,
        has_habit_match=True,
    )
    assert intent == "custom_habit_creation"


def test_gratitude_has_priority_over_habit() -> None:
    intent = classify_text_intent(
        session_state=SESSION_STATES["IDLE"],
        looks_gratitude=True,
        has_habit_match=True,
    )
    assert intent == "gratitude_list"


def test_habit_after_gratitude() -> None:
    intent = classify_text_intent(
        session_state=SESSION_STATES["IDLE"],
        looks_gratitude=False,
        has_habit_match=True,
    )
    assert intent == "habit_completion"
