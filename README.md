# Telegram Habit & Gratitude Bot (MVP)

Psychologically safe Telegram bot for:
- micro-habits
- gratitude journaling
- weekly supportive summaries
- optional weekly feelings notes

## Quick Start

1. Create and activate virtual env.
2. Install dependencies:
   - `pip install -e .[dev]`
3. Copy env:
   - `copy .env.example .env`
4. Fill `BOT_TOKEN` and `DATABASE_URL`.
5. Run bot:
   - `python -m src.app.main`

## Stack

- Python 3.11+
- aiogram
- SQLAlchemy (async)
- PostgreSQL (production), SQLite (tests)
- Alembic migrations
- APScheduler jobs

## Main Architecture

- `src/telegram`: command/text/callback handlers
- `src/domain`: business logic services
- `src/storage`: models/repositories/db session
- `src/messaging`: message engine for `messages.json`
- `src/jobs`: reminders, weekly summary, inactivity checks

## Core Product Guarantees

- no pressure / no shaming language
- timezone-aware daily and weekly logic
- idempotent reminders and weekly summary sends
- no duplicate habit completion in a single day
- all user-facing text sourced via `messages.json`
