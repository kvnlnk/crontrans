"""Natural language templates for generating cron expressions.

Maps keyword patterns found in user descriptions to cron field components.
"""
# Each template is a dict with:
#   - pattern: keywords/regex hints for matching
#   - fields: dict with minute, hour, dom, month, dow (each a cron field string)
#   - description: English description of what this template matches

TEMPLATES = [
    # ── Every minute ──────────────────────────────────────────
    {
        "pattern": ["every minute", "every 1 minute", "per minute", "each minute"],
        "fields": {"minute": "*", "hour": "*", "dom": "*", "month": "*", "dow": "*"},
        "description": "Every minute",
    },
    # ── Every N minutes ───────────────────────────────────────
    {
        "pattern": ["every {} minutes", "every {} min", "each {} minutes", "per {} minutes"],
        "fields": {"minute": "*/{}", "hour": "*", "dom": "*", "month": "*", "dow": "*"},
        "description": "Every {N} minutes",
        "numeric": True,
        "field": "minute",
    },
    # ── Every N hours ─────────────────────────────────────────
    {
        "pattern": ["every {} hours", "every {} hour", "each {} hours", "per {} hours"],
        "fields": {"minute": "0", "hour": "*/{}", "dom": "*", "month": "*", "dow": "*"},
        "description": "Every {N} hours",
        "numeric": True,
        "field": "hour",
    },
    # ── At HH:MM ──────────────────────────────────────────────
    {
        "pattern": ["at {}:{:02d}", "at {}:{:02d} {}", "at {}:{}", "at {}:{} {}"],
        "fields": {"minute": "{:02d}", "hour": "{}", "dom": "*", "month": "*", "dow": "*"},
        "description": "At {HH}:{MM}",
        "time_pattern": True,
    },
    # ── At HH:MM AM/PM ────────────────────────────────────────
    {
        "pattern": ["at {} {}"],
        "fields": {"minute": "0", "hour": "{}", "dom": "*", "month": "*", "dow": "*"},
        "description": "At {hour} {am/pm}",
        "hour_meridiem": True,
    },
    # ── Hourly ────────────────────────────────────────────────
    {
        "pattern": ["hourly", "every hour", "each hour"],
        "fields": {"minute": "0", "hour": "*", "dom": "*", "month": "*", "dow": "*"},
        "description": "Every hour",
    },
    # ── Daily ─────────────────────────────────────────────────
    {
        "pattern": ["daily", "every day", "each day", "once a day", "once per day"],
        "fields": {"minute": "0", "hour": "0", "dom": "*", "month": "*", "dow": "*"},
        "description": "Daily at midnight",
    },
    # ── Daily at specific time ────────────────────────────────
    {
        "pattern": ["daily at {}:{:02d}", "daily at {}:{}", "every day at {}:{:02d}"],
        "fields": {"minute": "{:02d}", "hour": "{}", "dom": "*", "month": "*", "dow": "*"},
        "description": "Daily at {HH}:{MM}",
        "time_pattern": True,
    },
    # ── Weekly ────────────────────────────────────────────────
    {
        "pattern": ["weekly", "once a week", "once per week"],
        "fields": {"minute": "0", "hour": "0", "dom": "*", "month": "*", "dow": "0"},
        "description": "Weekly on Sunday at midnight",
    },
    # ── Monthly ───────────────────────────────────────────────
    {
        "pattern": ["monthly", "once a month", "once per month"],
        "fields": {"minute": "0", "hour": "0", "dom": "1", "month": "*", "dow": "*"},
        "description": "Monthly on the 1st at midnight",
    },
    # ── Yearly ────────────────────────────────────────────────
    {
        "pattern": ["yearly", "annually", "once a year", "once per year"],
        "fields": {"minute": "0", "hour": "0", "dom": "1", "month": "1", "dow": "*"},
        "description": "Yearly on January 1st at midnight",
    },
    # ── Weekdays ──────────────────────────────────────────────
    {
        "pattern": ["weekdays", "weekday", "on weekdays", "every weekday", "during the week"],
        "fields": {"minute": "0", "hour": "0", "dom": "*", "month": "*", "dow": "1-5"},
        "description": "Weekdays at midnight",
    },
    # ── Weekends ──────────────────────────────────────────────
    {
        "pattern": ["weekends", "weekend", "on weekends", "every weekend"],
        "fields": {"minute": "0", "hour": "0", "dom": "*", "month": "*", "dow": "0,6"},
        "description": "Weekends at midnight",
    },
    # ── Specific day of week ──────────────────────────────────
    {
        "pattern": [
            "every {}", "on {}", "each {}",
            "every {} at", "on {} at",
        ],
        "fields": {"minute": "0", "hour": "0", "dom": "*", "month": "*", "dow": "{}"},
        "description": "Every {day} at midnight",
        "day_name": True,
    },
    # ── At HH on specific day ─────────────────────────────────
    {
        "pattern": ["at {} on {}", "at {} every {}", "at {} each {}"],
        "fields": {"minute": "0", "hour": "{}", "dom": "*", "month": "*", "dow": "{}"},
        "description": "At {hour} on {day}",
        "hour_and_day": True,
    },
    # ── At HH:MM on specific day ──────────────────────────────
    {
        "pattern": ["at {}:{:02d} on {}", "at {}:{} on {}", "at {}:{:02d} every {}"],
        "fields": {"minute": "{:02d}", "hour": "{}", "dom": "*", "month": "*", "dow": "{}"},
        "description": "At {HH}:{MM} on {day}",
        "time_and_day": True,
    },
    # ── On day Nth of month ───────────────────────────────────
    {
        "pattern": [
            "on the {} of the month", "on the {} of each month",
            "on day {} of the month", "monthly on the {}",
        ],
        "fields": {"minute": "0", "hour": "0", "dom": "{}", "month": "*", "dow": "*"},
        "description": "Monthly on the {N}th at midnight",
        "ordinal_day": True,
    },
    # ── At HH:MM on day Nth ───────────────────────────────────
    {
        "pattern": [
            "at {}:{:02d} on the {} of the month",
            "at {}:{} on the {} of the month",
        ],
        "fields": {"minute": "{:02d}", "hour": "{}", "dom": "{}", "month": "*", "dow": "*"},
        "description": "At {HH}:{MM} on the {N}th",
        "time_and_ordinal": True,
    },
]

# Day name to cron day-of-week number
DAY_NAME_TO_NUM = {
    "sunday": 0,
    "monday": 1,
    "tuesday": 2,
    "wednesday": 3,
    "thursday": 4,
    "friday": 5,
    "saturday": 6,
    "sun": 0,
    "mon": 1,
    "tue": 2,
    "wed": 3,
    "thu": 4,
    "fri": 5,
    "sat": 6,
}

# Ordinal to number
ORDINAL_TO_NUM = {
    "1st": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5,
    "6th": 6, "7th": 7, "8th": 8, "9th": 9, "10th": 10,
    "11th": 11, "12th": 12, "13th": 13, "14th": 14, "15th": 15,
    "16th": 16, "17th": 17, "18th": 18, "19th": 19, "20th": 20,
    "21st": 21, "22nd": 22, "23rd": 23, "24th": 24, "25th": 25,
    "26th": 26, "27th": 27, "28th": 28, "29th": 29, "30th": 30,
    "31st": 31,
}

# Also map plain numbers (these get handled differently in the generate code)
# But we support both "1st" and "1" forms
for n in range(1, 32):
    ORDINAL_TO_NUM[str(n)] = n
