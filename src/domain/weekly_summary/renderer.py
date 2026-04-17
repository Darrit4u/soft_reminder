from __future__ import annotations

from src.domain.gratitude.service import WeeklyGratitudeStats
from src.domain.habits.service import WeeklyHabitStats
from src.messaging.message_engine import MessageEngine


class WeeklySummaryRenderer:
    def __init__(self, message_engine: MessageEngine) -> None:
        self._message_engine = message_engine

    def _render_gratitude_block(self, user_id: str, stats: WeeklyGratitudeStats) -> str:
        template = self._message_engine.get_message(
            "weekly_summary.gratitude_block.templates", user_id=user_id
        )
        return self._message_engine.render_template(
            template,
            {
                "total_items": stats.total_items,
                "avg_per_day": f"{stats.avg_per_day:.1f}",
                "max_items_day": stats.max_items_day,
            },
        )

    def _render_habits_block(self, user_id: str, stats: WeeklyHabitStats) -> str:
        chunks: list[str] = []
        for item in stats.habits:
            base_template = self._message_engine.get_message(
                "weekly_summary.habits_block.item_templates", user_id=user_id
            )
            streak_template = self._message_engine.get_message(
                "weekly_summary.habits_block.streak_templates", user_id=user_id
            )
            item_text = self._message_engine.render_template(
                base_template,
                {
                    "habit_name": item.habit_name,
                    "completed_days": item.completed_days,
                    "total_days": item.total_days,
                    "completion_rate": item.completion_rate,
                },
            )
            streak_text = self._message_engine.render_template(
                streak_template,
                {"current_streak": item.current_streak, "best_streak": item.best_streak},
            )
            chunks.append(f"{item_text}\n{streak_text}")
        return "\n\n".join(chunks)

    def render(
        self,
        user_id: str,
        week_type: str,
        gratitude_stats: WeeklyGratitudeStats,
        habit_stats: WeeklyHabitStats,
        feeling_text: str | None,
    ) -> str:
        parts: list[str] = []
        parts.append(
            self._message_engine.get_message(f"weekly_summary.header.{week_type}", user_id=user_id)
        )

        if gratitude_stats.total_items > 0:
            parts.append(self._render_gratitude_block(user_id, gratitude_stats))
            parts.append(
                self._message_engine.get_message(
                    f"weekly_summary.interpreters.gratitude.{gratitude_stats.dynamic_type}",
                    user_id=user_id,
                )
            )

        if habit_stats.habits:
            parts.append(self._render_habits_block(user_id, habit_stats))
            parts.append(
                self._message_engine.get_message(
                    f"weekly_summary.interpreters.habits.{habit_stats.strong_type}",
                    user_id=user_id,
                )
            )
            if habit_stats.most_consistent_habit_name:
                parts.append(
                    self._message_engine.get_message(
                        "habits.weekly_summary.most_consistent",
                        user_id=user_id,
                        placeholders={"habit_name": habit_stats.most_consistent_habit_name},
                    )
                )
            if habit_stats.has_adaptation_habits:
                parts.append(
                    self._message_engine.get_message(
                        "habits.weekly_summary.adaptation_note", user_id=user_id
                    )
                )

        if feeling_text:
            tmpl = self._message_engine.get_message(
                "weekly_summary.feelings_block.templates", user_id=user_id
            )
            parts.append(
                self._message_engine.render_template(tmpl, {"feeling_text": feeling_text})
            )

        parts.append(
            self._message_engine.get_message(f"weekly_summary.closing.{week_type}", user_id=user_id)
        )
        return "\n\n".join([p for p in parts if p.strip()])
