from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone as dt_timezone
from zoneinfo import ZoneInfo


@dataclass(slots=True, frozen=True)
class WeekRange:
    start_date: str
    end_date: str


def now_utc() -> datetime:
    return datetime.now(dt_timezone.utc)


def to_user_tz(dt: datetime, tz_name: str) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dt_timezone.utc)
    return dt.astimezone(ZoneInfo(tz_name))


def user_now(tz_name: str, now: datetime | None = None) -> datetime:
    base = now or now_utc()
    return to_user_tz(base, tz_name)


def user_today_str(tz_name: str, now: datetime | None = None) -> str:
    return user_now(tz_name, now).date().isoformat()


def parse_hhmm(value: str) -> time:
    hour_s, minute_s = value.split(":", maxsplit=1)
    return time(hour=int(hour_s), minute=int(minute_s))


def within_window(local_dt: datetime, start_hhmm: str, end_hhmm: str) -> bool:
    current = local_dt.time()
    return parse_hhmm(start_hhmm) <= current <= parse_hhmm(end_hhmm)


def detect_window(local_dt: datetime, windows: dict[str, tuple[str, str]]) -> str | None:
    for name, (start, end) in windows.items():
        if within_window(local_dt, start, end):
            return name
    return None


def get_week_range_for_date(day: date) -> WeekRange:
    monday = day - timedelta(days=day.weekday())
    sunday = monday + timedelta(days=6)
    return WeekRange(start_date=monday.isoformat(), end_date=sunday.isoformat())


def get_week_range_for_user(tz_name: str, now: datetime | None = None) -> WeekRange:
    local_day = user_now(tz_name, now).date()
    return get_week_range_for_date(local_day)


def list_dates(start_date: str, end_date: str) -> list[str]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    out: list[str] = []
    cur = start
    while cur <= end:
        out.append(cur.isoformat())
        cur += timedelta(days=1)
    return out


def inactive_days(last_activity_at: datetime | None, tz_name: str, now: datetime | None = None) -> int:
    if last_activity_at is None:
        return 9999
    local_now = user_now(tz_name, now).date()
    local_last = to_user_tz(last_activity_at, tz_name).date()
    return (local_now - local_last).days
