from __future__ import annotations

import re

from src.utils.text import looks_like_numbered_list_line

_NUMBERED_LINE_RE = re.compile(r"^\s*\d+[\.\)]\s+(.+)$")


def parse_gratitude_items(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.split("\n") if line.strip()]
    if not lines:
        return []

    has_numbering = any(looks_like_numbered_list_line(line) for line in lines)
    items: list[str] = []

    if has_numbering:
        for line in lines:
            match = _NUMBERED_LINE_RE.match(line)
            if match:
                item = match.group(1).strip()
                if item:
                    items.append(item)
            else:
                items.append(line)
        return [item for item in items if item]

    return lines


def looks_like_gratitude_list(text: str, waiting_for_gratitude: bool = False) -> bool:
    if waiting_for_gratitude:
        return True
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.split("\n") if line.strip()]
    if len(lines) >= 2:
        return True
    return any(looks_like_numbered_list_line(line) for line in lines)
