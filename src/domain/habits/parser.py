from __future__ import annotations

from src.storage.models import Habit
from src.utils.text import normalize_text

HABIT_SYNONYMS = {
    "сделать короткую зарядку": ["зарядка", "сделал зарядку", "размялся", "размялась"],
    "выпить стакан воды утром": ["выпил воду", "выпила воду", "вода", "стакан воды"],
    "почистить зубы": ["почистил зубы", "почистила зубы", "зубы"],
    "умыться": ["умылся", "умылась", "умыл лицо", "умыла лицо"],
}

COMPLETION_VERBS = {"сделал", "сделала", "выполнил", "выполнила", "закрыл", "готово", "done"}


def _habit_signatures(habit: Habit) -> set[str]:
    normalized_title = normalize_text(habit.title)
    signatures = {normalized_title}
    signatures.update(HABIT_SYNONYMS.get(normalized_title, []))
    return {normalize_text(s) for s in signatures if s}


def detect_habit_completion(text: str, active_habits: list[Habit]) -> Habit | None:
    norm = normalize_text(text)
    if not norm:
        return None

    matched: list[Habit] = []
    for habit in active_habits:
        signatures = _habit_signatures(habit)
        if any(sig and sig in norm for sig in signatures):
            matched.append(habit)

    if len(matched) == 1:
        return matched[0]
    if len(matched) > 1:
        return None

    tokens = set(norm.split())
    if not tokens.intersection(COMPLETION_VERBS):
        return None

    for habit in active_habits:
        words = set(normalize_text(habit.title).split())
        if words and words.intersection(tokens):
            matched.append(habit)

    if len(matched) == 1:
        return matched[0]
    return None
