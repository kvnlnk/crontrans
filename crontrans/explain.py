"""Cron to English translation.

Takes a parsed cron expression and produces a human-readable English description.
"""

from .constants import DAY_NAMES, MONTH_NAMES, FIELD_RANGES
from .parser import parse_cron, expand_field


def _format_time(hour: int, minute: int) -> str:
    """Format a time like '9:00 AM' or '12:30 PM'."""
    period = "AM" if hour < 12 else "PM"
    if hour == 0:
        display_hour = 12
    elif hour > 12:
        display_hour = hour - 12
    else:
        display_hour = hour
    return f"{display_hour}:{minute:02d} {period}"


def _format_days_list(days: list) -> str:
    """Format a list of day numbers into an English list."""
    names = [DAY_NAMES[d] for d in sorted(days)]
    if len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return f"{names[0]} and {names[1]}"
    else:
        return ", ".join(names[:-1]) + f", and {names[-1]}"


def _format_months_list(months: list) -> str:
    """Format a list of month numbers into an English list."""
    names = [MONTH_NAMES[m] for m in sorted(months)]
    if len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return f"{names[0]} and {names[1]}"
    else:
        return ", ".join(names[:-1]) + f", and {names[-1]}"


def explain_cron(expression: str) -> str:
    """Translate a cron expression to an English description.

    Args:
        expression: A 5-field cron expression string.

    Returns:
        A human-readable English string describing the schedule.

    Raises:
        ValueError: If the expression is invalid.
    """
    parsed = parse_cron(expression)
    minute = parsed["minute"]
    hour = parsed["hour"]
    dom = parsed["dom"]
    month = parsed["month"]
    dow = parsed["dow"]

    minute_is_all = minute["type"] == "any"
    hour_is_all = hour["type"] == "any"
    dom_is_all = dom["type"] == "any"
    month_is_all = month["type"] == "any"
    dow_is_all = dow["type"] == "any"

    # CASE 1: Every minute
    if minute_is_all and hour_is_all and dom_is_all and month_is_all and dow_is_all:
        return "Every minute"

    # CASE 2: Every N minutes
    if minute["type"] == "step" and hour_is_all and dom_is_all and month_is_all and dow_is_all:
        step = minute["step"]
        return f"Every {step} minutes"

    # CASE 3: Every N hours (at minute 0)
    if minute["type"] == "value" and minute["value"] == 0 and hour["type"] == "step" and dom_is_all and month_is_all and dow_is_all:
        step = hour["step"]
        return f"Every {step} hours"

    # CASE 4: Every N hours at specific minute
    if minute["type"] == "value" and hour["type"] == "step" and dom_is_all and month_is_all and dow_is_all:
        step = hour["step"]
        m = minute["value"]
        if m == 0:
            return f"Every {step} hours"
        return f"At {m} minutes past the hour, every {step} hours"

    # Build time description
    time_desc = _describe_time(minute, hour)
    if time_desc is None:
        # If time is complex, just describe the time part
        if not minute_is_all or not hour_is_all:
            time_desc = _describe_time_fallback(minute, hour)

    # Build day description
    day_desc = _describe_days(dow, dom, month)

    # CASE: Hourly (at specific minute)
    if minute["type"] == "value" and hour_is_all and dom_is_all and month_is_all and dow_is_all:
        m = minute["value"]
        if m == 0:
            return "At the top of every hour"
        return f"At {m} minutes past every hour"

    # CASE: Every N minutes on specific days
    if minute["type"] == "step":
        step = minute["step"]
        prefix = f"Every {step} minutes"
        if day_desc:
            return f"{prefix}, {day_desc}"
        return prefix

    # CASE: Specific time on specific days (most common pattern)
    if time_desc and day_desc:
        return f"{time_desc}, {day_desc}"

    # CASE: Only time specified, no day restriction
    if time_desc and not day_desc:
        return time_desc

    # CASE: Only days specified, no time restriction
    if not time_desc and day_desc:
        return f"Every minute, {day_desc}"

    # Fallback - should rarely be reached
    return f"Cron expression: {expression}"


def _describe_time(minute: dict, hour: dict) -> str | None:
    """Describe the time component if it's a specific time or simple pattern.

    Returns None if the time is complex (not a simple description).
    """
    # Single specific time: minute + hour both single values
    if minute["type"] == "value" and hour["type"] == "value":
        return f"At {_format_time(hour['value'], minute['value'])}"

    # Multiple specific times (list of hours, exact minute)
    if minute["type"] == "value" and hour["type"] == "list":
        times = [_format_time(h, minute["value"]) for h in sorted(hour["values"])]
        if len(times) == 2:
            return f"At {times[0]} and {times[1]}"
        return "At " + ", ".join(times[:-1]) + f", and {times[-1]}"

    # Range of hours with exact minute
    if minute["type"] == "value" and hour["type"] == "range":
        start = _format_time(hour["start"], minute["value"])
        end = _format_time(hour["end"], minute["value"])
        return f"Every hour from {start} through {end}"

    # Multiple minutes with single hour
    if minute["type"] == "list" and hour["type"] == "value":
        minutes = sorted(minute["values"])
        times = [_format_time(hour["value"], m) for m in minutes]
        if len(times) == 2:
            return f"At {times[0]} and {times[1]}"
        return "At " + ", ".join(times[:-1]) + f", and {times[-1]}"

    return None


def _describe_time_fallback(minute: dict, hour: dict) -> str | None:
    """Fallback time description for complex patterns."""
    parts = []

    # Describe minute
    if minute["type"] == "any":
        parts.append("every minute")
    elif minute["type"] == "value":
        parts.append(f"at minute {minute['value']}")
    elif minute["type"] == "step":
        parts.append(f"every {minute['step']} minutes")
    elif minute["type"] == "list":
        mins = sorted(minute["values"])
        parts.append(f"at minutes {', '.join(str(m) for m in mins)}")
    elif minute["type"] == "range":
        parts.append(f"from minute {minute['start']} to {minute['end']}")

    # Describe hour
    if hour["type"] == "any":
        parts.append("of every hour")
    elif hour["type"] == "value":
        parts.append(f"past hour {hour['value']}")
    elif hour["type"] == "step":
        parts.append(f"every {hour['step']} hours")
    elif hour["type"] == "list":
        hrs = sorted(hour["values"])
        parts.append(f"at hours {', '.join(str(h) for h in hrs)}")

    if parts:
        return " ".join(parts).capitalize()
    return None


def _describe_days(dow: dict, dom: dict, month: dict) -> str | None:
    """Describe the day/month component."""
    dow_is_all = dow["type"] == "any"
    dom_is_all = dom["type"] == "any"
    month_is_all = month["type"] == "any"

    # Both dom and dow specified
    if not dom_is_all and not dow_is_all:
        dom_desc = _describe_dom(dom)
        dow_desc = _describe_dow(dow)
        month_desc = _describe_month(month)
        parts = []
        if dom_desc:
            parts.append(dom_desc)
        if month_desc:
            parts.append(month_desc)
        if dow_desc:
            parts.append(dow_desc)
        if parts:
            return ", ".join(parts)
        return None

    # Day of week specific
    if not dow_is_all:
        dow_desc = _describe_dow(dow)
        month_desc = _describe_month(month)
        if month_desc:
            return f"{dow_desc}, only in {month_desc}"
        return dow_desc

    # Day of month specific
    if not dom_is_all:
        dom_desc = _describe_dom(dom)
        month_desc = _describe_month(month)
        if month_desc:
            return f"{dom_desc}, only in {month_desc}"
        return dom_desc

    # Month specific only
    if not month_is_all:
        month_desc = _describe_month(month)
        return f"only in {month_desc}"

    return None


def _describe_dow(dow: dict) -> str | None:
    """Describe day-of-week field."""
    t = dow["type"]

    if t == "any":
        return None

    if t == "value":
        return f"only on {DAY_NAMES[dow['value']]}"

    if t == "range":
        start = DAY_NAMES[dow["start"]]
        end = DAY_NAMES[dow["end"]]
        # Check for weekdays (1-5) and weekends (0,6 or 6,0) and
        # special common ranges
        if dow["start"] == 1 and dow["end"] == 5:
            return "Monday through Friday"
        if dow["start"] == 0 and dow["end"] == 6:
            return "every day"
        return f"{start} through {end}"

    if t == "list":
        days = sorted(dow["values"])
        # Check for weekends (0 and 6)
        if days == [0, 6]:
            return "only on weekends"
        if days == [0]:
            return "only on Sunday"
        if days == [6]:
            return "only on Saturday"
        return f"only on {_format_days_list(days)}"

    return None


def _describe_dom(dom: dict) -> str | None:
    """Describe day-of-month field."""
    t = dom["type"]

    if t == "any":
        return None

    if t == "value":
        v = dom["value"]
        suffix = "th"
        if v % 10 == 1 and v != 11:
            suffix = "st"
        elif v % 10 == 2 and v != 12:
            suffix = "nd"
        elif v % 10 == 3 and v != 13:
            suffix = "rd"
        return f"on day {v}{suffix} of the month"

    if t == "range":
        return f"on days {dom['start']} through {dom['end']} of the month"

    if t == "list":
        days = sorted(dom["values"])
        return f"on days {', '.join(str(d) for d in days)} of the month"

    return None


def _describe_month(month: dict) -> str | None:
    """Describe month field."""
    t = month["type"]

    if t == "any":
        return None

    if t == "value":
        return MONTH_NAMES[month["value"]]

    if t == "range":
        start = MONTH_NAMES[month["start"]]
        end = MONTH_NAMES[month["end"]]
        return f"{start} through {end}"

    if t == "list":
        return _format_months_list(month["values"])

    return None
