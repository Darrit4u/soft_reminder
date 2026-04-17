from datetime import datetime, timezone

from src.utils.dates import get_week_range_for_user


def test_week_range_is_iso_monday_sunday() -> None:
    # Monday in Europe/Berlin
    now = datetime(2026, 4, 13, 12, 0, tzinfo=timezone.utc)
    week = get_week_range_for_user("Europe/Berlin", now=now)
    assert week.start_date == "2026-04-13"
    assert week.end_date == "2026-04-19"
