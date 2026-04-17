from __future__ import annotations

import asyncio
import logging

from src.app.bootstrap import build_application
from src.config.env import Settings
from src.utils.logger import configure_logging


async def run() -> None:
    configure_logging()
    settings = Settings.from_env()
    bot, dispatcher, _, scheduler = await build_application(settings)
    scheduler.start()
    logging.getLogger(__name__).info("Bot started in polling mode")
    try:
        await dispatcher.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(run())
