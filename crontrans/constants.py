"""Constants for cron field ranges, day names, and month names."""

# Field ranges
MIN_RANGE = (0, 59)
HOUR_RANGE = (0, 23)
DOM_RANGE = (1, 31)
MONTH_RANGE = (1, 12)
DOW_RANGE = (0, 6)

FIELD_NAMES = ["minute", "hour", "day of month", "month", "day of week"]

FIELD_RANGES = {
    "minute": MIN_RANGE,
    "hour": HOUR_RANGE,
    "day of month": DOM_RANGE,
    "month": MONTH_RANGE,
    "day of week": DOW_RANGE,
}

FIELD_ORDER = ["minute", "hour", "dom", "month", "dow"]

# Day names
DAY_NAMES = {
    0: "Sunday",
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
}

DOW_ABBR = {
    0: "Sun",
    1: "Mon",
    2: "Tue",
    3: "Wed",
    4: "Thu",
    5: "Fri",
    6: "Sat",
}

# Month names
MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

MONTH_ABBR = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}
