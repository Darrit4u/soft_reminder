from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(slots=True)
class Settings:
    bot_token: str
    database_url: str
    bot_mode: str = "polling"
    default_timezone: str = "Europe/Berlin"
    default_locale: str = "ru"
    weekly_summary_day: int = 7
    weekly_summary_time: str = "19:00"
    run_migrations_on_start: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        bot_token = os.getenv("BOT_TOKEN", "").strip()
        if not bot_token:
            raise ValueError("BOT_TOKEN is required")
        return cls(
            bot_token=bot_token,
            database_url=os.getenv(
                "DATABASE_URL",
                "postgresql+asyncpg://postgres:postgres@localhost:5432/habitbot",
            ),
            bot_mode=os.getenv("BOT_MODE", "polling"),
            default_timezone=os.getenv("DEFAULT_TIMEZONE", "Europe/Berlin"),
            default_locale=os.getenv("DEFAULT_LOCALE", "ru"),
            weekly_summary_day=_as_int(os.getenv("WEEKLY_SUMMARY_DAY"), 7),
            weekly_summary_time=os.getenv("WEEKLY_SUMMARY_TIME", "19:00"),
            run_migrations_on_start=_as_bool(
                os.getenv("RUN_MIGRATIONS_ON_START"), default=False
            ),
        )
