from __future__ import annotations

import re


_SPACES_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s]+", re.UNICODE)
_EMOJI_ONLY_RE = re.compile(r"^[\W_]+$", re.UNICODE)


def normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    lowered = _PUNCT_RE.sub(" ", lowered)
    lowered = _SPACES_RE.sub(" ", lowered)
    return lowered.strip()


def is_probably_emoji_only(text: str) -> bool:
    if not text.strip():
        return False
    return bool(_EMOJI_ONLY_RE.match(text.strip()))


def looks_like_numbered_list_line(text: str) -> bool:
    return bool(re.match(r"^\s*\d+[\.\)]\s+.+$", text))
