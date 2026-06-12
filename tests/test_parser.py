"""Tests for the cron expression parser."""

import pytest

from crontrans.parser import (
    parse_field,
    expand_field,
    parse_cron,
    validate_cron,
    format_cron,
)


class TestParseField:
    """Tests for parse_field()."""

    def test_wildcard(self):
        result = parse_field("*", 0, 59)
        assert result == {"type": "any"}

    def test_step_every_5(self):
        result = parse_field("*/5", 0, 59)
        assert result == {"type": "step", "step": 5}

    def test_step_every_15(self):
        result = parse_field("*/15", 0, 59)
        assert result == {"type": "step", "step": 15}

    def test_range(self):
        result = parse_field("1-5", 0, 6)
        assert result == {"type": "range", "start": 1, "end": 5}

    def test_range_single_value(self):
        result = parse_field("3-3", 0, 59)
        assert result == {"type": "range", "start": 3, "end": 3}

    def test_list(self):
        result = parse_field("1,3,5", 0, 6)
        assert result == {"type": "list", "values": [1, 3, 5]}

    def test_list_two_values(self):
        result = parse_field("0,30", 0, 59)
        assert result == {"type": "list", "values": [0, 30]}

    def test_single_value(self):
        result = parse_field("30", 0, 59)
        assert result == {"type": "value", "value": 30}

    def test_single_value_zero(self):
        result = parse_field("0", 0, 59)
        assert result == {"type": "value", "value": 0}

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="empty"):
            parse_field("", 0, 59)

    def test_whitespace_string_raises(self):
        with pytest.raises(ValueError, match="empty"):
            parse_field("   ", 0, 59)

    def test_step_zero_raises(self):
        with pytest.raises(ValueError, match="positive"):
            parse_field("*/0", 0, 59)

    def test_step_negative_raises(self):
        with pytest.raises(ValueError, match="positive"):
            parse_field("*/-5", 0, 59)

    def test_step_exceeds_range_raises(self):
        with pytest.raises(ValueError, match="exceeds"):
            parse_field("*/100", 0, 59)

    def test_range_start_outside_low(self):
        with pytest.raises(ValueError, match="outside"):
            parse_field("-1-5", 0, 59)

    def test_range_end_outside_high(self):
        with pytest.raises(ValueError, match="outside"):
            parse_field("0-60", 0, 59)

    def test_range_start_greater_than_end(self):
        with pytest.raises(ValueError, match="greater"):
            parse_field("5-3", 0, 59)

    def test_list_value_out_of_range(self):
        with pytest.raises(ValueError, match="outside"):
            parse_field("1,99", 0, 59)

    def test_invalid_pattern(self):
        with pytest.raises(ValueError, match="Unrecognized"):
            parse_field("abc", 0, 59)

    def test_invalid_pattern_symbols(self):
        with pytest.raises(ValueError, match="Unrecognized"):
            parse_field("5%3", 0, 59)

    def test_boundary_min(self):
        result = parse_field("0", 0, 59)
        assert result == {"type": "value", "value": 0}

    def test_boundary_max(self):
        result = parse_field("59", 0, 59)
        assert result == {"type": "value", "value": 59}

    def test_month_names_not_supported(self):
        """Month names like JAN are not supported by parser."""
        with pytest.raises(ValueError, match="Unrecognized"):
            parse_field("JAN", 1, 12)


class TestExpandField:
    """Tests for expand_field()."""

    def test_any(self):
        result = expand_field({"type": "any"}, 0, 59)
        assert result == list(range(0, 60))

    def test_step_every_15(self):
        result = expand_field({"type": "step", "step": 15}, 0, 59)
        assert result == [0, 15, 30, 45]

    def test_step_every_30(self):
        result = expand_field({"type": "step", "step": 30}, 0, 59)
        assert result == [0, 30]

    def test_range(self):
        result = expand_field({"type": "range", "start": 1, "end": 5}, 0, 6)
        assert result == [1, 2, 3, 4, 5]

    def test_list(self):
        result = expand_field({"type": "list", "values": [0, 15, 30, 45]}, 0, 59)
        assert result == [0, 15, 30, 45]

    def test_list_unsorted(self):
        result = expand_field({"type": "list", "values": [30, 15, 45]}, 0, 59)
        assert result == [15, 30, 45]

    def test_value(self):
        result = expand_field({"type": "value", "value": 30}, 0, 59)
        assert result == [30]

    def test_dom_range(self):
        result = expand_field({"type": "range", "start": 1, "end": 15}, 1, 31)
        assert result == list(range(1, 16))


class TestParseCron:
    """Tests for parse_cron()."""

    def test_every_5_minutes(self):
        result = parse_cron("*/5 * * * *")
        assert result["minute"] == {"type": "step", "step": 5}
        assert result["hour"] == {"type": "any"}
        assert result["dom"] == {"type": "any"}
        assert result["month"] == {"type": "any"}
        assert result["dow"] == {"type": "any"}

    def test_daily_at_9am_weekdays(self):
        result = parse_cron("0 9 * * 1-5")
        assert result["minute"] == {"type": "value", "value": 0}
        assert result["hour"] == {"type": "value", "value": 9}
        assert result["dow"] == {"type": "range", "start": 1, "end": 5}

    def test_specific_time_list_days(self):
        result = parse_cron("30 4 * * 1,3,5")
        assert result["minute"] == {"type": "value", "value": 30}
        assert result["hour"] == {"type": "value", "value": 4}
        assert result["dow"] == {"type": "list", "values": [1, 3, 5]}

    def test_yearly(self):
        result = parse_cron("0 0 1 1 *")
        assert result["minute"] == {"type": "value", "value": 0}
        assert result["hour"] == {"type": "value", "value": 0}
        assert result["dom"] == {"type": "value", "value": 1}
        assert result["month"] == {"type": "value", "value": 1}

    def test_every_hour(self):
        result = parse_cron("0 * * * *")
        assert result["minute"] == {"type": "value", "value": 0}
        assert result["hour"] == {"type": "any"}

    def test_every_minute(self):
        result = parse_cron("* * * * *")
        for key in ["minute", "hour", "dom", "month", "dow"]:
            assert result[key] == {"type": "any"}

    def test_every_30_minutes(self):
        result = parse_cron("*/30 * * * *")
        assert result["minute"] == {"type": "step", "step": 30}

    def test_twice_daily(self):
        result = parse_cron("0 9,21 * * *")
        assert result["hour"] == {"type": "list", "values": [9, 21]}

    def test_weekly_wednesday(self):
        result = parse_cron("0 0 * * 3")
        assert result["dow"] == {"type": "value", "value": 3}

    def test_monthly_first(self):
        result = parse_cron("0 0 1 * *")
        assert result["dom"] == {"type": "value", "value": 1}

    def test_weekends(self):
        result = parse_cron("0 0 * * 0,6")
        assert result["dow"] == {"type": "list", "values": [0, 6]}

    def test_invalid_field_count_too_few(self):
        with pytest.raises(ValueError, match="exactly 5 fields"):
            parse_cron("*/5 * * *")

    def test_invalid_field_count_too_many(self):
        with pytest.raises(ValueError, match="exactly 5 fields"):
            parse_cron("*/5 * * * * extra")

    def test_empty_expression(self):
        with pytest.raises(ValueError, match="exactly 5 fields"):
            parse_cron("")

    def test_invalid_minute(self):
        with pytest.raises(ValueError, match="Invalid minute"):
            parse_cron("abc * * * *")

    def test_invalid_hour(self):
        with pytest.raises(ValueError, match="Invalid hour"):
            parse_cron("0 25 * * *")

    def test_invalid_dom(self):
        with pytest.raises(ValueError, match="Invalid day of month"):
            parse_cron("0 0 32 * *")

    def test_invalid_month(self):
        with pytest.raises(ValueError, match="Invalid month"):
            parse_cron("0 0 1 13 *")

    def test_invalid_dow(self):
        with pytest.raises(ValueError, match="Invalid day of week"):
            parse_cron("0 0 * * 7")


class TestValidateCron:
    """Tests for validate_cron()."""

    def test_valid(self):
        # Should not raise
        validate_cron("*/5 * * * *")
        validate_cron("0 9 * * 1-5")
        validate_cron("30 4 * * 1,3,5")

    def test_invalid_field_count(self):
        with pytest.raises(ValueError):
            validate_cron("*/5 * * *")

    def test_invalid_field_value(self):
        with pytest.raises(ValueError):
            validate_cron("*/5 25 * * *")

    def test_empty(self):
        with pytest.raises(ValueError):
            validate_cron("")


class TestFormatCron:
    """Tests for format_cron()."""

    def test_every_5_minutes(self):
        parsed = parse_cron("*/5 * * * *")
        assert format_cron(parsed) == "*/5 * * * *"

    def test_daily_at_9am_weekdays(self):
        parsed = parse_cron("0 9 * * 1-5")
        assert format_cron(parsed) == "0 9 * * 1-5"

    def test_specific_time_list_days(self):
        parsed = parse_cron("30 4 * * 1,3,5")
        assert format_cron(parsed) == "30 4 * * 1,3,5"

    def test_every_minute(self):
        parsed = parse_cron("* * * * *")
        assert format_cron(parsed) == "* * * * *"

    def test_yearly(self):
        parsed = parse_cron("0 0 1 1 *")
        assert format_cron(parsed) == "0 0 1 1 *"
