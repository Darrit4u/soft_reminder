from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine

from src.storage.base import Base
from src.storage import models  # noqa: F401


async def create_all_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
