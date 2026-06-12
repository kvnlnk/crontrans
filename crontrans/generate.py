"""English to cron translation.

Takes a natural language description and produces the matching cron expression.
Uses template-based keyword matching to handle ~30 common patterns.
"""

import re

from .templates import TEMPLATES, DAY_NAME_TO_NUM, ORDINAL_TO_NUM
from .parser import validate_cron


def _parse_time_from_text(text: str) -> tuple | None:
    """Try to extract a time (HH:MM, H:MM AM/PM, H AM/PM) from text.

    Returns (hour_24, minute) or None.
    """
    # Pattern: HH:MM AM/PM or H:MM AM/PM
    m = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm|a\.m\.|p\.m\.)", text, re.IGNORECASE)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2))
        meridiem = m.group(3).lower()[0]
        if meridiem == "p" and hour != 12:
            hour += 12
        elif meridiem == "a" and hour == 12:
            hour = 0
        return (hour, minute)

    # Pattern: HH:MM (24h)
    m = re.search(r"(\d{1,2}):(\d{2})\b", text)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return (hour, minute)

    # Pattern: H AM/PM or HH AM/PM (without minutes)
    m = re.search(r"(\d{1,2})\s*(am|pm|a\.m\.|p\.m\.)", text, re.IGNORECASE)
    if m:
        hour = int(m.group(1))
        meridiem = m.group(2).lower()[0]
        if meridiem == "p" and hour != 12:
            hour += 12
        elif meridiem == "a" and hour == 12:
            hour = 0
        return (hour, 0)

    return None


def _parse_day_from_text(text: str) -> int | None:
    """Extract a day name from text and return its cron number (0-6)."""
    text_lower = text.lower()
    for name, num in DAY_NAME_TO_NUM.items():
        if name in text_lower:
            return num
    return None


def _parse_ordinal_from_text(text: str) -> int | None:
    """Extract an ordinal day number (1st, 2nd, etc.) from text."""
    text_lower = text.lower().strip()
    # Try the full text first
    if text_lower in ORDINAL_TO_NUM:
        return ORDINAL_TO_NUM[text_lower]
    # Search within the text
    m = re.search(r"\b(\d+(?:st|nd|rd|th))\b", text_lower)
    if m:
        key = m.group(1)
        if key in ORDINAL_TO_NUM:
            return ORDINAL_TO_NUM[key]
    # Also try bare numbers
    m = re.search(r"\bthe (\d+)(?:st|nd|rd|th)?\b", text_lower)
    if m:
        num = int(m.group(1))
        if 1 <= num <= 31:
            return num
    return None


def _extract_number(text: str) -> int | None:
    """Extract a number from text (like '5' from 'every 5 minutes')."""
    m = re.search(r"\b(\d+)\b", text)
    if m:
        return int(m.group(1))
    return None


def generate_cron(nl_description: str) -> str:
    """Generate a cron expression from a natural language description.

    Args:
        nl_description: A plain English description of a schedule.

    Returns:
        A 5-field cron expression string.

    Raises:
        ValueError: If the description cannot be parsed into a cron expression.
    """
    text = nl_description.strip().lower()

    if not text:
        raise ValueError("Empty description")

    # ── Try direct template patterns first ──────────────────

    # 1. "every minute" / "every 1 minute"
    if text in ("every minute", "every 1 minute", "per minute", "each minute"):
        return "* * * * *"

    # 2. "hourly" / "every hour" / "each hour"
    if text in ("hourly", "every hour", "each hour"):
        return "0 * * * *"

    # 3. "daily" / "every day" / "each day" / "once a day" / "once per day"
    if text in ("daily", "every day", "each day", "once a day", "once per day"):
        return "0 0 * * *"

    # 4. "weekly" / "once a week" / "once per week"
    if text in ("weekly", "once a week", "once per week"):
        return "0 0 * * 0"

    # 5. "monthly" / "once a month" / "once per month"
    if text in ("monthly", "once a month", "once per month"):
        return "0 0 1 * *"

    # 6. "yearly" / "annually" / "once a year" / "once per year"
    if text in ("yearly", "annually", "once a year", "once per year"):
        return "0 0 1 1 *"

    # 7. "weekdays" / "weekday" / "on weekdays" / "every weekday"
    if text in ("weekdays", "weekday", "on weekdays", "every weekday", "during the week"):
        return "0 0 * * 1-5"

    # 8. "weekends" / "weekend" / "on weekends" / "every weekend"
    if text in ("weekends", "weekend", "on weekends", "every weekend"):
        return "0 0 * * 0,6"

    # ── Pattern: "every N minutes" ────────────────────
    m = re.search(r"every\s+(\d+)\s+minutes?", text)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 59:
            return f"*/{n} * * * *"

    # ── Pattern: "every N hours" ──────────────────────
    m = re.search(r"every\s+(\d+)\s+hours?", text)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 23:
            return f"0 */{n} * * *"

    # ── Parse time and day components ──────────────────

    time = _parse_time_from_text(text)
    day_num = _parse_day_from_text(text)
    ordinal = _parse_ordinal_from_text(text)

    hour_val, minute_val = None, None
    if time:
        hour_val, minute_val = time

    # Check if it's a weekdays/weekends + time pattern
    is_weekday = any(w in text for w in ["weekday", "week days", "week-days"])
    is_weekend = any(w in text for w in ["weekend", "week ends", "week-ends"])
    is_daily = any(w in text for w in ["daily", "every day", "each day"])

    # ── Build cron fields ──────────────────────────

    # Default fields
    minute = "*"
    hour = "*"
    dom = "*"
    month = "*"
    dow = "*"

    # Set time
    if hour_val is not None:
        minute = f"{minute_val:02d}"
        hour = str(hour_val)
    elif time is not None:
        minute = f"{minute_val:02d}"
        hour = str(hour_val)
    else:
        # Check for "at" without explicit time → try to extract just hour
        m = re.search(r"at\s+(\d{1,2})\b", text)
        if m:
            h = int(m.group(1))
            # If followed by am/pm, already handled; otherwise assume 24h
            if 0 <= h <= 23:
                hour = str(h)
                minute = "0"

    # Set day of week
    if day_num is not None:
        dow = str(day_num)
    elif is_weekday:
        dow = "1-5"
    elif is_weekend:
        dow = "0,6"

    # Set day of month
    if ordinal is not None:
        dom = str(ordinal)

    # Nothing specific was parsed
    if hour == "*" and minute == "*" and dom == "*" and dow == "*":
        raise ValueError(
            f"Cannot parse '{nl_description}'. Try a description like "
            f"'every 5 minutes', 'daily at 9am', or 'weekdays at 3:30 PM'."
        )

    # Build cron string
    cron = f"{minute} {hour} {dom} {month} {dow}"

    # Validate
    try:
        validate_cron(cron)
    except ValueError as e:
        raise ValueError(
            f"Generated invalid cron from '{nl_description}': {e}"
        ) from e

    return cron
