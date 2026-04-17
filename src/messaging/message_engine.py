from __future__ import annotations

import json
import random
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


class MessageEngine:
    _template_re = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

    def __init__(self, messages_path: str | Path, history_limit: int = 10) -> None:
        self._messages_path = Path(messages_path)
        self._messages = self._load_messages()
        self._history_limit = history_limit
        self._recent_by_user: dict[str, deque[str]] = defaultdict(
            lambda: deque(maxlen=history_limit)
        )

    def _load_messages(self) -> dict[str, Any]:
        return json.loads(self._messages_path.read_text(encoding="utf-8"))

    def get_raw(self, path: str) -> Any:
        node: Any = self._messages
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                raise KeyError(f"Message path not found: {path}")
            node = node[part]
        return node

    def get_list(self, path: str) -> list[str]:
        node = self.get_raw(path)
        if not isinstance(node, list):
            raise TypeError(f"Path {path} is not a list")
        return [str(item) for item in node]

    def get_message(
        self,
        path: str,
        placeholders: dict[str, str | int | float] | None = None,
        user_id: str | None = None,
        exclude_recent: list[str] | None = None,
        fallback: str | None = None,
    ) -> str:
        try:
            node = self.get_raw(path)
        except (KeyError, TypeError):
            if fallback is not None:
                return fallback
            return path

        if isinstance(node, list):
            selected = self._get_random_variant(node, user_id=user_id, exclude_recent=exclude_recent)
        elif isinstance(node, str):
            selected = node
        else:
            if fallback is not None:
                return fallback
            return path

        if placeholders:
            selected = self.render_template(selected, placeholders)
        return selected

    def _get_random_variant(
        self,
        items: list[str],
        user_id: str | None = None,
        exclude_recent: list[str] | None = None,
    ) -> str:
        if not items:
            return ""
        candidates = list(items)
        excluded = set(exclude_recent or [])
        if user_id:
            excluded.update(self._recent_by_user[user_id])
        filtered = [item for item in candidates if item not in excluded]
        pool = filtered if filtered else candidates
        selected = random.choice(pool)
        if user_id:
            self._recent_by_user[user_id].append(selected)
        return selected

    def render_template(self, template: str, placeholders: dict[str, str | int | float]) -> str:
        def _replace(match: re.Match[str]) -> str:
            key = match.group(1)
            value = placeholders.get(key)
            return "" if value is None else str(value)

        return self._template_re.sub(_replace, template)

    def validate_paths(self, required_paths: list[str]) -> list[str]:
        missing: list[str] = []
        for path in required_paths:
            try:
                self.get_raw(path)
            except Exception:
                missing.append(path)
        return missing
