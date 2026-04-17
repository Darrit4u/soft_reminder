from src.domain.gratitude.parser import looks_like_gratitude_list, parse_gratitude_items


def test_parse_numbered_gratitude_items() -> None:
    text = "1. Спасибо за сон\n2) Спасибо за чай\n3. Спасибо за прогулку"
    items = parse_gratitude_items(text)
    assert items == ["Спасибо за сон", "Спасибо за чай", "Спасибо за прогулку"]


def test_parse_line_based_gratitude_items() -> None:
    text = "Спасибо за музыку\nСпасибо за друга\nСпасибо за отдых"
    items = parse_gratitude_items(text)
    assert len(items) == 3


def test_parse_single_line_fallback() -> None:
    text = "Спасибо за то, что получилось встать утром"
    items = parse_gratitude_items(text)
    assert items == ["Спасибо за то, что получилось встать утром"]


def test_looks_like_gratitude_detection() -> None:
    assert looks_like_gratitude_list("1. Спасибо", waiting_for_gratitude=False)
    assert looks_like_gratitude_list("Строка 1\nСтрока 2", waiting_for_gratitude=False)
    assert not looks_like_gratitude_list("сделал зарядку", waiting_for_gratitude=False)
