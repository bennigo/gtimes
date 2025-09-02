"""Unit tests for time function utilities."""

import datetime
import numpy as np
import pytest

from gtimes.timefunc import (
    dTimetoYearf,
    TimetoYearf,
    TimefromYearf,
    currDatetime,
    currDate,
    DayofYear,
    DaysinYear,
    shifTime,
    round_to_hour,
    convfromYearf,
)


class TestFractionalYear:
    """Test fractional year conversions."""

    def test_datetime_to_yearf(self):
        """Test conversion from datetime to fractional year."""
        dt = datetime.datetime(2020, 1, 1, 12, 0, 0)
        yearf = dTimetoYearf(dt)
        
        # Should be close to 2020.0 (middle of first day)
        assert 2020.0 <= yearf <= 2020.01

    def test_components_to_yearf(self):
        """Test conversion from date components to fractional year."""
        yearf = TimetoYearf(2020, 1, 1, 12, 0, 0)
        assert 2020.0 <= yearf <= 2020.01
        
        # Mid-year should be around .5
        yearf_mid = TimetoYearf(2020, 7, 1, 12, 0, 0)
        assert 2020.4 < yearf_mid < 2020.6

    def test_yearf_to_datetime(self):
        """Test conversion from fractional year to datetime."""
        yearf = 2020.5  # Mid-year
        dt = TimefromYearf(yearf)
        
        assert isinstance(dt, datetime.datetime)
        assert dt.year == 2020
        # Should be around mid-year
        assert 5 <= dt.month <= 8

    def test_yearf_roundtrip(self):
        """Test roundtrip conversion datetime -> yearf -> datetime."""
        original_dt = datetime.datetime(2020, 6, 15, 14, 30, 45)
        
        # Convert to fractional year and back
        yearf = dTimetoYearf(original_dt)
        recovered_dt = TimefromYearf(yearf)
        
        # Should be very close (within a second)
        time_diff = abs((recovered_dt - original_dt).total_seconds())
        assert time_diff < 1.0

    def test_yearf_string_formats(self):
        """Test fractional year with different string output formats."""
        yearf = 2020.5
        
        # Test ordinalf format
        ordinalf = TimefromYearf(yearf, String="ordinalf")
        assert isinstance(ordinalf, float)
        
        # Test datetime string format
        date_str = TimefromYearf(yearf, String="%Y-%m-%d")
        assert isinstance(date_str, str)
        assert "2020" in date_str

    def test_round_to_hour(self):
        """Test hour rounding functionality."""
        yearf = 2020.5
        
        # Test without rounding
        dt_normal = TimefromYearf(yearf)
        
        # Test with rounding
        dt_rounded = TimefromYearf(yearf, rhour=True)
        
        assert dt_rounded.minute == 0
        assert dt_rounded.second == 0
        assert dt_rounded.microsecond == 0


class TestRoundToHour:
    """Test the round_to_hour function."""

    def test_round_down(self):
        """Test rounding down when minutes < 30."""
        dt = datetime.datetime(2020, 1, 1, 12, 25, 30)
        rounded = round_to_hour(dt)
        
        assert rounded == datetime.datetime(2020, 1, 1, 12, 0, 0)

    def test_round_up(self):
        """Test rounding up when minutes >= 30."""
        dt = datetime.datetime(2020, 1, 1, 12, 35, 30)
        rounded = round_to_hour(dt)
        
        assert rounded == datetime.datetime(2020, 1, 1, 13, 0, 0)

    def test_round_exactly_30(self):
        """Test rounding when exactly 30 minutes."""
        dt = datetime.datetime(2020, 1, 1, 12, 30, 0)
        rounded = round_to_hour(dt)
        
        assert rounded == datetime.datetime(2020, 1, 1, 13, 0, 0)

    def test_midnight_rollover(self):
        """Test rounding that crosses midnight."""
        dt = datetime.datetime(2020, 1, 1, 23, 45, 0)
        rounded = round_to_hour(dt)
        
        assert rounded == datetime.datetime(2020, 1, 2, 0, 0, 0)


class TestCurrentDatetime:
    """Test current datetime functions."""

    def test_curr_datetime_default(self):
        """Test currDatetime with default parameters."""
        dt = currDatetime()
        assert isinstance(dt, datetime.datetime)
        
        # Should be close to now
        now = datetime.datetime.today()
        time_diff = abs((dt - now).total_seconds())
        assert time_diff < 5  # Within 5 seconds

    def test_curr_datetime_with_offset(self):
        """Test currDatetime with day offset."""
        dt_plus_1 = currDatetime(days=1)
        dt_minus_1 = currDatetime(days=-1)
        dt_now = currDatetime()
        
        # Check offsets are correct
        assert (dt_plus_1 - dt_now).days == 1
        assert (dt_now - dt_minus_1).days == 1

    def test_curr_date_default(self):
        """Test currDate with default parameters."""
        date = currDate()
        assert isinstance(date, datetime.date)
        
        # Should be today
        today = datetime.date.today()
        assert date == today


class TestUtilityFunctions:
    """Test utility functions."""

    def test_day_of_year(self):
        """Test day of year calculation."""
        # January 1st is day 1
        assert DayofYear(year=2020, month=1, day=1) == 1
        
        # December 31st in leap year
        assert DayofYear(year=2020, month=12, day=31) == 366
        
        # December 31st in non-leap year
        assert DayofYear(year=2021, month=12, day=31) == 365

    def test_days_in_year(self):
        """Test days in year calculation."""
        assert DaysinYear(2020) == 366  # Leap year
        assert DaysinYear(2021) == 365  # Non-leap year
        assert DaysinYear(1900) == 365  # Century year, not leap
        assert DaysinYear(2000) == 366  # Century year, is leap

    def test_shift_time(self):
        """Test time shifting string parsing."""
        # Test default
        shift = shifTime()
        assert shift["days"] == 0.0
        
        # Test single day shift
        shift = shifTime("d1")
        assert shift["days"] == 1.0
        
        # Test complex shift
        shift = shifTime("d1:H2:M30")
        assert shift["days"] == 1.0
        assert shift["hours"] == 2.0
        assert shift["minutes"] == 30.0

    def test_shift_time_numeric_input(self):
        """Test shifTime with numeric input."""
        shift = shifTime(5)  # Should become "d5"
        assert shift["days"] == 5.0


class TestVectorization:
    """Test numpy array vectorization functions."""

    def test_conv_from_yearf_array(self):
        """Test conversion from fractional year array."""
        yearf_array = np.array([2020.0, 2020.25, 2020.5, 2020.75])
        
        # Convert to datetime objects
        dt_array = convfromYearf(yearf_array)
        
        assert isinstance(dt_array, np.ndarray)
        assert len(dt_array) == len(yearf_array)
        
        # All should be datetime objects
        for dt in dt_array:
            assert isinstance(dt, datetime.datetime)
        
        # All should be in 2020
        for dt in dt_array:
            assert dt.year == 2020

    def test_conv_from_yearf_with_format(self):
        """Test conversion with string formatting."""
        yearf_array = np.array([2020.0, 2020.5])
        
        # Convert to date strings
        str_array = convfromYearf(yearf_array, String="%Y-%m-%d")
        
        assert isinstance(str_array, np.ndarray)
        
        # All should be strings
        for date_str in str_array:
            assert isinstance(date_str, str)
            assert "2020" in date_str

    def test_conv_from_yearf_with_rounding(self):
        """Test conversion with hour rounding."""
        yearf_array = np.array([2020.0])
        
        # Convert with hour rounding
        dt_array = convfromYearf(yearf_array, rhour=True)
        
        dt = dt_array[0]
        assert dt.minute == 0
        assert dt.second == 0
        assert dt.microsecond == 0


@pytest.mark.parametrize("year", [2000, 2004, 2020, 2024])  # Mix of leap and non-leap years
def test_leap_year_calculations(year):
    """Test calculations work correctly for leap years."""
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    expected_days = 366 if is_leap else 365
    
    assert DaysinYear(year) == expected_days
    
    # Test fractional year conversion for end of year
    yearf_end = TimetoYearf(year, 12, 31, 23, 59, 59)
    assert yearf_end > year + 0.99  # Should be very close to next year


@pytest.mark.parametrize("month,day,expected_doy", [
    (1, 1, 1),      # New Year's Day
    (3, 1, 60),     # March 1st in non-leap year (59 + 1)
    (7, 4, 185),    # July 4th
    (12, 31, 365),  # End of non-leap year
])
def test_day_of_year_known_values(month, day, expected_doy):
    """Test day of year for known values in a non-leap year."""
    # Test for 2021 (non-leap year)
    doy = DayofYear(year=2021, month=month, day=day)
    assert doy == expected_doy