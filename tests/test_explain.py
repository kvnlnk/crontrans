"""Tests for the cron explain (cron → English) module."""

import pytest

from crontrans.explain import explain_cron


class TestExplainEveryMinute:
    def test_every_minute(self):
        assert explain_cron("* * * * *") == "Every minute"


class TestExplainStepMinutes:
    def test_every_5_minutes(self):
        assert explain_cron("*/5 * * * *") == "Every 5 minutes"

    def test_every_15_minutes(self):
        assert explain_cron("*/15 * * * *") == "Every 15 minutes"

    def test_every_30_minutes(self):
        assert explain_cron("*/30 * * * *") == "Every 30 minutes"

    def test_every_10_minutes(self):
        assert explain_cron("*/10 * * * *") == "Every 10 minutes"


class TestExplainStepHours:
    def test_every_2_hours(self):
        assert explain_cron("0 */2 * * *") == "Every 2 hours"

    def test_every_6_hours(self):
        assert explain_cron("0 */6 * * *") == "Every 6 hours"

    def test_every_12_hours(self):
        assert explain_cron("0 */12 * * *") == "Every 12 hours"


class TestExplainHourly:
    def test_at_top_of_every_hour(self):
        assert explain_cron("0 * * * *") == "At the top of every hour"

    def test_at_30_past_every_hour(self):
        assert explain_cron("30 * * * *") == "At 30 minutes past every hour"


class TestExplainDaily:
    def test_daily_midnight(self):
        assert explain_cron("0 0 * * *") == "At 12:00 AM"

    def test_daily_9am(self):
        assert explain_cron("0 9 * * *") == "At 9:00 AM"

    def test_daily_3pm(self):
        assert explain_cron("0 15 * * *") == "At 3:00 PM"

    def test_daily_noon(self):
        assert explain_cron("0 12 * * *") == "At 12:00 PM"

    def test_daily_3_30pm(self):
        assert explain_cron("30 15 * * *") == "At 3:30 PM"

    def test_daily_1_05am(self):
        assert explain_cron("5 1 * * *") == "At 1:05 AM"


class TestExplainWeekdays:
    def test_weekdays_9am(self):
        assert explain_cron("0 9 * * 1-5") == "At 9:00 AM, Monday through Friday"

    def test_weekdays_midnight(self):
        assert explain_cron("0 0 * * 1-5") == "At 12:00 AM, Monday through Friday"

    def test_weekdays_5pm(self):
        assert explain_cron("0 17 * * 1-5") == "At 5:00 PM, Monday through Friday"


class TestExplainWeekends:
    def test_weekends_midnight(self):
        result = explain_cron("0 0 * * 0,6")
        assert "12:00 AM" in result
        assert "weekends" in result

    def test_weekends_9am(self):
        result = explain_cron("0 9 * * 0,6")
        assert "9:00 AM" in result
        assert "weekends" in result


class TestExplainSpecificDays:
    def test_monday_only(self):
        assert explain_cron("0 9 * * 1") == "At 9:00 AM, only on Monday"

    def test_wednesday_only(self):
        assert explain_cron("0 0 * * 3") == "At 12:00 AM, only on Wednesday"

    def test_monday_wednesday_friday(self):
        result = explain_cron("30 4 * * 1,3,5")
        assert "4:30 AM" in result
        assert "Monday" in result
        assert "Wednesday" in result
        assert "Friday" in result

    def test_tuesday_thursday(self):
        result = explain_cron("0 14 * * 2,4")
        assert "2:00 PM" in result
        assert "Tuesday" in result
        assert "Thursday" in result


class TestExplainMonthly:
    def test_first_of_month_midnight(self):
        assert explain_cron("0 0 1 * *") == "At 12:00 AM, on day 1st of the month"

    def test_15th_of_month_noon(self):
        assert explain_cron("0 12 15 * *") == "At 12:00 PM, on day 15th of the month"

    def test_2nd_of_month_3am(self):
        assert explain_cron("0 3 2 * *") == "At 3:00 AM, on day 2nd of the month"

    def test_3rd_of_month(self):
        assert explain_cron("0 0 3 * *") == "At 12:00 AM, on day 3rd of the month"


class TestExplainYearly:
    def test_yearly_jan_1st(self):
        assert explain_cron("0 0 1 1 *") == "At 12:00 AM, on day 1st of the month, only in January"

    def test_christmas(self):
        assert explain_cron("0 0 25 12 *") == "At 12:00 AM, on day 25th of the month, only in December"


class TestExplainMultipleTimes:
    def test_twice_daily_9am_9pm(self):
        result = explain_cron("0 9,21 * * *")
        assert "9:00 AM" in result
        assert "9:00 PM" in result

    def test_three_times_daily(self):
        result = explain_cron("0 6,12,18 * * *")
        assert "6:00 AM" in result
        assert "12:00 PM" in result
        assert "6:00 PM" in result


class TestExplainComplex:
    def test_every_30_minutes_weekdays(self):
        assert explain_cron("*/30 * * * 1-5") == "Every 30 minutes, Monday through Friday"

    def test_every_15_minutes_weekends(self):
        result = explain_cron("*/15 * * * 0,6")
        assert "Every 15 minutes" in result
        assert "weekends" in result

    def test_monthly_on_1st_and_15th(self):
        result = explain_cron("0 9 1,15 * *")
        assert "9:00 AM" in result
        assert "1" in result
        assert "15" in result

    def test_quarterly_hours(self):
        """Every 15 minutes during 9-5."""
        result = explain_cron("*/15 9-17 * * *")
        assert "Every 15 minutes" in result or "every" in result


class TestExplainErrors:
    def test_invalid_expression(self):
        with pytest.raises(ValueError):
            explain_cron("invalid cron")

    def test_empty_string(self):
        with pytest.raises(ValueError):
            explain_cron("")
