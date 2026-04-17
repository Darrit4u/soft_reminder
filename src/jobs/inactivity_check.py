from __future__ import annotations

import logging

from src.app.types import AppServices

logger = logging.getLogger(__name__)


async def run_inactivity_check(services: AppServices) -> None:
    users = await services.user_service.list_users()
    for user in users:
        try:
            new_state = services.engagement_service.get_engagement_state(
                last_activity_at=user.last_activity_at,
                timezone=user.timezone,
            )
            if new_state != user.engagement_state:
                await services.user_service.update_engagement_state(user.id, new_state)
        except Exception:
            logger.exception("inactivity check failed for user_id=%s", user.id)
