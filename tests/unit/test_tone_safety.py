import json
from pathlib import Path


FORBIDDEN = [
    "Ты не сделал",
    "Почему ты не ответил",
    "Нужно стараться больше",
    "Ты опять пропустил",
    "Ты должен",
    "Надо обязательно",
]


def _collect_strings(node) -> list[str]:
    if isinstance(node, str):
        return [node]
    if isinstance(node, list):
        out: list[str] = []
        for item in node:
            out.extend(_collect_strings(item))
        return out
    if isinstance(node, dict):
        out: list[str] = []
        for value in node.values():
            out.extend(_collect_strings(value))
        return out
    return []


def test_messages_do_not_contain_forbidden_shaming_patterns() -> None:
    data = json.loads(Path("messages.json").read_text(encoding="utf-8"))
    all_strings = _collect_strings(data)
    joined = "\n".join(all_strings)
    for phrase in FORBIDDEN:
        assert phrase not in joined
