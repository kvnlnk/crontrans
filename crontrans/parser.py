"""Cron expression parser.

Parses a 5-field cron expression into a structured dict of parsed fields.
Each field is a dict with a 'type' key and additional keys depending on type.
"""

import re

from .constants import FIELD_NAMES, FIELD_RANGES, FIELD_ORDER

# Regex patterns for field types
RE_STEP = re.compile(r"^\*\/(\d+)$")
RE_RANGE = re.compile(r"^(\d+)-(\d+)$")
RE_LIST = re.compile(r"^(\d+)(?:,(\d+))+$")
RE_VALUE = re.compile(r"^\d+$")


def parse_field(field_str: str, min_val: int, max_val: int) -> dict:
    """Parse a single cron field string.

    Args:
        field_str: The field string (e.g., '*', '*/5', '1-5', '1,3,5', '0')
        min_val: Minimum valid value for this field
        max_val: Maximum valid value for this field

    Returns:
        dict with 'type' key and additional data:
        - type 'any': {'type': 'any'}  (*)
        - type 'step': {'type': 'step', 'step': N}  (*/N)
        - type 'range': {'type': 'range', 'start': N, 'end': N}  (N-M)
        - type 'list': {'type': 'list', 'values': [N, ...]}  (N,M)
        - type 'value': {'type': 'value', 'value': N}  (N)

    Raises:
        ValueError: If the field string is invalid or contains out-of-range values.
    """
    field_str = field_str.strip()

    if not field_str:
        raise ValueError("Field string is empty")

    # Step: */N
    m = RE_STEP.match(field_str)
    if m:
        step = int(m.group(1))
        if step <= 0:
            raise ValueError(f"Step value must be positive, got {step}")
        if step > (max_val - min_val + 1):
            raise ValueError(
                f"Step value {step} exceeds field range ({min_val}-{max_val})"
            )
        return {"type": "step", "step": step}

    # Range: N-M
    m = RE_RANGE.match(field_str)
    if m:
        start = int(m.group(1))
        end = int(m.group(2))
        if start < min_val or start > max_val:
            raise ValueError(
                f"Range start {start} is outside valid range ({min_val}-{max_val})"
            )
        if end < min_val or end > max_val:
            raise ValueError(
                f"Range end {end} is outside valid range ({min_val}-{max_val})"
            )
        if start > end:
            raise ValueError(
                f"Range start {start} is greater than range end {end}"
            )
        return {"type": "range", "start": start, "end": end}

    # List: N,M
    if "," in field_str:
        parts = field_str.split(",")
        values = []
        for p in parts:
            p = p.strip()
            if not RE_VALUE.match(p):
                raise ValueError(f"Invalid list item '{p}'")
            val = int(p)
            if val < min_val or val > max_val:
                raise ValueError(
                    f"Value {val} is outside valid range ({min_val}-{max_val})"
                )
            values.append(val)
        if len(values) < 2:
            raise ValueError(f"List must have at least 2 values, got {field_str}")
        return {"type": "list", "values": values}

    # Wildcard: *
    if field_str == "*":
        return {"type": "any"}

    # Single value: N
    if RE_VALUE.match(field_str):
        val = int(field_str)
        if val < min_val or val > max_val:
            raise ValueError(
                f"Value {val} is outside valid range ({min_val}-{max_val})"
            )
        return {"type": "value", "value": val}

    raise ValueError(f"Unrecognized field pattern: '{field_str}'")


def expand_field(parsed: dict, min_val: int, max_val: int) -> list:
    """Expand a parsed field into a sorted list of integer values.

    Args:
        parsed: Output from parse_field()
        min_val: Minimum valid value
        max_val: Maximum valid value

    Returns:
        Sorted list of integers representing all matching values.
        Returns an empty list for 'any' type (caller handles * specially).
    """
    t = parsed["type"]
    if t == "any":
        return list(range(min_val, max_val + 1))
    elif t == "step":
        step = parsed["step"]
        return list(range(min_val, max_val + 1, step))
    elif t == "range":
        return list(range(parsed["start"], parsed["end"] + 1))
    elif t == "list":
        return sorted(parsed["values"])
    elif t == "value":
        return [parsed["value"]]
    else:
        raise ValueError(f"Unknown field type: {t}")


def parse_cron(expression: str) -> dict:
    """Parse a full 5-field cron expression.

    Args:
        expression: A cron expression string (e.g., "*/5 * * * *")

    Returns:
        dict with keys: minute, hour, dom, month, dow
        Each value is a parsed field dict from parse_field().

    Raises:
        ValueError: If the expression is invalid.
    """
    parts = expression.strip().split()

    if len(parts) != 5:
        raise ValueError(
            f"Cron expression must have exactly 5 fields, got {len(parts)} "
            f"(expected format: minute hour dom month dow)"
        )

    ranges = [
        ("minute", *FIELD_RANGES["minute"]),
        ("hour", *FIELD_RANGES["hour"]),
        ("dom", *FIELD_RANGES["day of month"]),
        ("month", *FIELD_RANGES["month"]),
        ("dow", *FIELD_RANGES["day of week"]),
    ]

    result = {}
    for i, (field_name, min_val, max_val) in enumerate(ranges):
        try:
            result[field_name] = parse_field(parts[i], min_val, max_val)
        except ValueError as e:
            raise ValueError(
                f"Invalid {FIELD_NAMES[i]} field '{parts[i]}': {e}"
            ) from e

    return result


def validate_cron(expression: str) -> None:
    """Validate a cron expression, raising ValueError with detailed error on failure.

    Args:
        expression: A cron expression string

    Raises:
        ValueError: If the expression is invalid, with a message indicating
                    which field failed.
    """
    # First check field count
    parts = expression.strip().split()
    if len(parts) != 5:
        raise ValueError(
            f"Cron expression must have exactly 5 fields, got {len(parts)}. "
            f"Usage: minute hour day-of-month month day-of-week"
        )

    # Parse each field to validate
    parse_cron(expression)


def format_cron(parsed: dict) -> str:
    """Format a parsed cron dict back into a cron expression string.

    Args:
        parsed: Dict with keys minute, hour, dom, month, dow, each being
                a parsed field dict.

    Returns:
        A 5-field cron expression string.
    """
    parts = []
    for key in FIELD_ORDER:
        field = parsed[key]
        t = field["type"]
        if t == "any":
            parts.append("*")
        elif t == "step":
            parts.append(f"*/{field['step']}")
        elif t == "range":
            parts.append(f"{field['start']}-{field['end']}")
        elif t == "list":
            parts.append(",".join(str(v) for v in field["values"]))
        elif t == "value":
            parts.append(str(field["value"]))
        else:
            parts.append("*")
    return " ".join(parts)
