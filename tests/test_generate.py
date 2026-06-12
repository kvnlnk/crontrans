"""Tests for the generate (English → cron) module."""

import pytest

from crontrans.generate import generate_cron


class TestGenerateEveryMinute:
    def test_every_minute(self):
        assert generate_cron("every minute") == "* * * * *"

    def test_every_1_minute(self):
        assert generate_cron("every 1 minute") == "* * * * *"

    def test_per_minute(self):
        assert generate_cron("per minute") == "* * * * *"


class TestGenerateStepMinutes:
    def test_every_5_minutes(self):
        assert generate_cron("every 5 minutes") == "*/5 * * * *"

    def test_every_15_minutes(self):
        assert generate_cron("every 15 minutes") == "*/15 * * * *"

    def test_every_30_minutes(self):
        assert generate_cron("every 30 minutes") == "*/30 * * * *"

    def test_every_10_minutes(self):
        assert generate_cron("every 10 minutes") == "*/10 * * * *"


class TestGenerateStepHours:
    def test_every_2_hours(self):
        assert generate_cron("every 2 hours") == "0 */2 * * *"

    def test_every_6_hours(self):
        assert generate_cron("every 6 hours") == "0 */6 * * *"


class TestGenerateHourly:
    def test_hourly(self):
        assert generate_cron("hourly") == "0 * * * *"

    def test_every_hour(self):
        assert generate_cron("every hour") == "0 * * * *"


class TestGenerateDaily:
    def test_daily(self):
        assert generate_cron("daily") == "0 0 * * *"

    def test_every_day(self):
        assert generate_cron("every day") == "0 0 * * *"

    def test_once_a_day(self):
        assert generate_cron("once a day") == "0 0 * * *"


class TestGenerateDailyAtTime:
    def test_daily_at_9am_12h(self):
        assert generate_cron("daily at 9am") == "0 9 * * *"

    def test_daily_at_3pm(self):
        assert generate_cron("daily at 3pm") == "0 15 * * *"

    def test_daily_at_midnight(self):
        assert generate_cron("daily at 12am") == "0 0 * * *"

    def test_daily_at_noon(self):
        assert generate_cron("daily at 12pm") == "0 12 * * *"

    def test_at_9am(self):
        assert generate_cron("at 9am") == "0 9 * * *"

    def test_at_3_30pm(self):
        assert generate_cron("at 3:30 PM") == "30 15 * * *"

    def test_at_9_15am(self):
        assert generate_cron("at 9:15 AM") == "15 9 * * *"

    def test_at_14_30(self):
        assert generate_cron("at 14:30") == "30 14 * * *"

    def test_at_00_00(self):
        assert generate_cron("at 00:00") == "0 0 * * *"


class TestGenerateWeekly:
    def test_weekly(self):
        assert generate_cron("weekly") == "0 0 * * 0"

    def test_once_a_week(self):
        assert generate_cron("once a week") == "0 0 * * 0"


class TestGenerateMonthly:
    def test_monthly(self):
        assert generate_cron("monthly") == "0 0 1 * *"

    def test_once_a_month(self):
        assert generate_cron("once a month") == "0 0 1 * *"


class TestGenerateYearly:
    def test_yearly(self):
        assert generate_cron("yearly") == "0 0 1 1 *"

    def test_annually(self):
        assert generate_cron("annually") == "0 0 1 1 *"

    def test_once_a_year(self):
        assert generate_cron("once a year") == "0 0 1 1 *"


class TestGenerateWeekdays:
    def test_weekdays(self):
        assert generate_cron("weekdays") == "0 0 * * 1-5"

    def test_on_weekdays(self):
        assert generate_cron("on weekdays") == "0 0 * * 1-5"

    def test_every_weekday(self):
        assert generate_cron("every weekday") == "0 0 * * 1-5"


class TestGenerateWeekends:
    def test_weekends(self):
        assert generate_cron("weekends") == "0 0 * * 0,6"

    def test_on_weekends(self):
        assert generate_cron("on weekends") == "0 0 * * 0,6"

    def test_every_weekend(self):
        assert generate_cron("every weekend") == "0 0 * * 0,6"


class TestGenerateWeekdaysAtTime:
    def test_weekdays_at_9am(self):
        result = generate_cron("weekdays at 9am")
        assert result == "0 9 * * 1-5"

    def test_weekdays_at_5pm(self):
        result = generate_cron("weekdays at 5pm")
        assert result == "0 17 * * 1-5"

    def test_weekdays_at_3_30pm(self):
        result = generate_cron("weekdays at 3:30 PM")
        assert result == "30 15 * * 1-5"

    def test_weekends_at_10am(self):
        result = generate_cron("weekends at 10am")
        assert result == "0 10 * * 0,6"

    def test_daily_at_9am(self):
        assert generate_cron("daily at 9am") == "0 9 * * *"


class TestGenerateSpecificDay:
    def test_every_monday(self):
        result = generate_cron("every Monday")
        assert result == "0 0 * * 1"

    def test_every_friday(self):
        result = generate_cron("every Friday")
        assert result == "0 0 * * 5"

    def test_every_sunday(self):
        result = generate_cron("every Sunday")
        assert result == "0 0 * * 0"

    def test_on_wednesday(self):
        result = generate_cron("on Wednesday")
        assert result == "0 0 * * 3"

    def test_every_monday_at_9am(self):
        result = generate_cron("every Monday at 9am")
        assert result == "0 9 * * 1"

    def test_on_tuesday_at_3_30pm(self):
        result = generate_cron("on Tuesday at 3:30 PM")
        assert result == "30 15 * * 2"

    def test_every_friday_at_5pm(self):
        result = generate_cron("every Friday at 5pm")
        assert result == "0 17 * * 5"


class TestGenerateOrdinalDay:
    def test_on_the_1st(self):
        result = generate_cron("on the 1st of the month")
        assert result == "0 0 1 * *"

    def test_on_the_15th(self):
        result = generate_cron("on the 15th of the month")
        assert result == "0 0 15 * *"

    def test_at_9am_on_1st(self):
        result = generate_cron("at 9am on the 1st of the month")
        assert result == "0 9 1 * *"

    def test_monthly_on_the_2nd(self):
        result = generate_cron("monthly on the 2nd")
        assert result == "0 0 2 * *"

    def test_monthly_on_the_31st(self):
        result = generate_cron("monthly on the 31st")
        assert result == "0 0 31 * *"


class TestGenerateRoundtrip:
    """Test that explain(generate(x)) is coherent."""

    def test_every_5_minutes_roundtrip(self):
        from crontrans.explain import explain_cron
        cron = generate_cron("every 5 minutes")
        explanation = explain_cron(cron)
        assert "Every" in explanation
        assert "5" in explanation

    def test_daily_9am_roundtrip(self):
        from crontrans.explain import explain_cron
        cron = generate_cron("daily at 9am")
        explanation = explain_cron(cron)
        assert "9:00 AM" in explanation

    def test_weekdays_roundtrip(self):
        from crontrans.explain import explain_cron
        cron = generate_cron("weekdays at 3:30 PM")
        explanation = explain_cron(cron)
        assert "3:30 PM" in explanation
        assert "Monday through Friday" in explanation


class TestGenerateErrors:
    def test_empty_description(self):
        with pytest.raises(ValueError, match="Empty"):
            generate_cron("")

    def test_gibberish(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            generate_cron("purple monkey dishwasher")

    def test_unparseable(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            generate_cron("do it whenever")
