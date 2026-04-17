from __future__ import annotations

ENGAGEMENT_THRESHOLDS = {
    "LOW_ACTIVITY_DAYS": 2,
    "INACTIVE_DAYS": 5,
}

WEEKLY_SUMMARY_DEFAULTS = {
    "DAY": 7,  # Sunday
    "TIME": "19:00",
}

GRATITUDE = {
    "SOFT_TARGET": 10,
    "STABILITY_THRESHOLD": 1.0,
}

REMINDERS = {
    "MAX_PER_DAY": 3,
    "WINDOWS": {
        "morning": ("08:00", "11:00"),
        "day": ("12:00", "16:00"),
        "evening": ("18:00", "21:00"),
    },
}

SESSION_STATES = {
    "IDLE": "idle",
    "WAITING_FOR_CUSTOM_HABIT": "waiting_for_custom_habit",
    "WAITING_FOR_GRATITUDE": "waiting_for_gratitude",
    "WAITING_FOR_WEEKLY_FEELINGS": "waiting_for_weekly_feelings",
}

CALLBACK_PREFIXES = {
    "HABIT_DONE": "habit_done",
    "ADD_HABIT_DEFAULT": "add_habit_default",
    "ADD_HABIT_CUSTOM": "add_habit_custom",
    "KEEP_CURRENT_HABITS": "keep_current_habits",
    "WRITE_WEEKLY_FEELINGS": "write_weekly_feelings",
}
