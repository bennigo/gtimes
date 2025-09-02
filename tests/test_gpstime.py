"""Unit tests for GPS time conversion functions."""

import datetime
import math
import pytest

from gtimes.gpstime import (
    UTCFromGps,
    GpsSecondsFromPyUTC,
    PyUTCFromGpsSeconds,
    dayOfWeek,
    gpsFromUTC,
    gpsWeek,
    julianDay,
    mkUTC,
    ymdhmsFromPyUTC,
    getleapSecs,
    leapSecDict,
)


class TestBasicConversions:
    """Test basic GPS time conversions."""

    def test_gps_epoch(self):
        """Test GPS epoch (1980-01-06 00:00:00 UTC) is GPS week 0, SOW 0."""
        gps_week, sow = gpsFromUTC(1980, 1, 6, 0, 0, 0)
        assert gps_week == 0
        assert sow == 0

    def test_known_gps_time(self):
        """Test a known GPS time conversion."""
        # Test date from GPS time documentation
        gps_week, sow = gpsFromUTC(2002, 10, 12, 8, 34, 12.3)
        
        # Convert back to UTC
        utc_dt = UTCFromGps(gps_week, sow, dtimeObj=True)
        
        assert utc_dt.year == 2002
        assert utc_dt.month == 10
        assert utc_dt.day == 12
        assert utc_dt.hour == 8
        assert utc_dt.minute == 34
        # Allow small tolerance for floating point precision
        assert abs(utc_dt.second + utc_dt.microsecond / 1e6 - 12.3) < 1e-6

    def test_roundtrip_conversion(self):
        """Test UTC to GPS to UTC roundtrip conversion."""
        test_dates = [
            (2000, 1, 1, 12, 0, 0),
            (2010, 6, 15, 18, 30, 45.5),
            (2020, 12, 31, 23, 59, 59.9),
            (1980, 1, 6, 0, 0, 0),  # GPS epoch
        ]
        
        for year, month, day, hour, minute, second in test_dates:
            # UTC to GPS
            gps_week, sow = gpsFromUTC(year, month, day, hour, minute, second)
            
            # GPS back to UTC
            utc_dt = UTCFromGps(gps_week, sow, dtimeObj=True)
            
            assert utc_dt.year == year
            assert utc_dt.month == month
            assert utc_dt.day == day
            assert utc_dt.hour == hour
            assert utc_dt.minute == minute
            assert abs(utc_dt.second + utc_dt.microsecond / 1e6 - second) < 1e-6


class TestYmdhmsFromPyUTC:
    """Test the fixed ymdhmsFromPyUTC function."""

    def test_fractional_seconds(self):
        """Test that fractional seconds are preserved."""
        # Create a UTC time with fractional seconds
        ymdhms = (2002, 10, 12, 8, 34, 12.3)
        pyUtc = mkUTC(*ymdhms)
        result = ymdhmsFromPyUTC(pyUtc)
        
        assert len(ymdhms) == len(result)
        for i, (expected, actual) in enumerate(zip(ymdhms, result)):
            if i < 5:  # year, month, day, hour, min are integers
                assert expected == actual
            else:  # seconds can have fractional part
                assert abs(expected - actual) < 1e-6

    def test_integer_seconds(self):
        """Test that integer seconds still work."""
        ymdhms = (2002, 10, 12, 8, 34, 12)
        pyUtc = mkUTC(*ymdhms)
        result = ymdhmsFromPyUTC(pyUtc)
        
        assert result == ymdhms


class TestUtilityFunctions:
    """Test utility functions."""

    def test_day_of_week(self):
        """Test day of week calculation."""
        # Test known dates
        assert dayOfWeek(2002, 10, 6) == 0  # Sunday
        assert dayOfWeek(2002, 10, 12) == 6  # Saturday
        
    def test_julian_day(self):
        """Test Julian day calculation."""
        assert julianDay(2000, 1, 1) == 1
        assert julianDay(2000, 12, 31) == 366  # Leap year
        assert julianDay(2001, 12, 31) == 365  # Non-leap year

    def test_gps_week_calculation(self):
        """Test GPS week number calculation."""
        # GPS epoch is week 0
        assert gpsWeek(1980, 1, 6) == 0
        
        # Test some known GPS weeks
        week_2000 = gpsWeek(2000, 1, 1)
        assert week_2000 > 0
        
        week_2020 = gpsWeek(2020, 1, 1)
        assert week_2020 > week_2000


class TestLeapSeconds:
    """Test leap second handling."""

    def test_leap_sec_dict(self):
        """Test that leap second dictionary has expected structure."""
        leap_dict = leapSecDict()
        
        assert isinstance(leap_dict, dict)
        assert len(leap_dict) > 0
        
        # Check some known leap second dates
        assert 1981 in leap_dict
        assert 1999 in leap_dict  # Last leap second before GPS time started using 18

    def test_get_leap_secs(self):
        """Test automatic leap second detection."""
        # Test with datetime object
        dt_2010 = datetime.datetime(2010, 1, 1)
        leap_2010 = getleapSecs(dt_2010)
        assert isinstance(leap_2010, int)
        assert leap_2010 > 0
        
        # Test without arguments (should use current time)
        leap_current = getleapSecs()
        assert isinstance(leap_current, int)
        assert leap_current > 0


class TestGpsSeconds:
    """Test GPS seconds conversion functions."""

    def test_gps_seconds_roundtrip(self):
        """Test conversion between Python UTC and GPS seconds."""
        test_dt = datetime.datetime(2010, 6, 15, 12, 30, 45, 500000)  # with microseconds
        pyutc = test_dt.timestamp()
        
        # Python UTC to GPS seconds
        gps_seconds = GpsSecondsFromPyUTC(pyutc)
        
        # GPS seconds back to Python UTC
        pyutc_back = PyUTCFromGpsSeconds(gps_seconds)
        
        # Should be very close (within microsecond precision)
        assert abs(pyutc - pyutc_back) < 1e-6

    def test_gps_seconds_vs_week_sow(self):
        """Test consistency between GPS seconds and week/SOW conversion."""
        year, month, day, hour, minute, second = 2010, 6, 15, 12, 30, 45.5
        
        # Get GPS week and SOW
        gps_week, sow = gpsFromUTC(year, month, day, hour, minute, second)
        
        # Get GPS seconds
        pyutc = mkUTC(year, month, day, hour, minute, second)
        gps_seconds = GpsSecondsFromPyUTC(pyutc)
        
        # Calculate GPS seconds from week and SOW
        gps_seconds_from_week = gps_week * 7 * 24 * 3600 + sow
        
        # Should be very close
        assert abs(gps_seconds - gps_seconds_from_week) < 1e-6


@pytest.mark.parametrize("year,month,day,hour,minute,second", [
    (1980, 1, 6, 0, 0, 0),      # GPS epoch
    (2000, 1, 1, 0, 0, 0),      # Y2K
    (2010, 6, 15, 12, 30, 45),  # Random date
    (2020, 2, 29, 23, 59, 59),  # Leap year edge case
    (2024, 12, 31, 23, 59, 59.999),  # High precision seconds
])
def test_parametrized_conversions(year, month, day, hour, minute, second):
    """Parametrized test for various date/time combinations."""
    # UTC to GPS conversion
    gps_week, sow = gpsFromUTC(year, month, day, hour, minute, second)
    
    # Verify GPS week is reasonable
    assert gps_week >= 0
    assert 0 <= sow < 7 * 24 * 3600  # SOW should be less than seconds in a week
    
    # Convert back and verify
    utc_dt = UTCFromGps(gps_week, sow, dtimeObj=True)
    assert utc_dt.year == year
    assert utc_dt.month == month
    assert utc_dt.day == day
    assert utc_dt.hour == hour
    assert utc_dt.minute == minute
    assert abs(utc_dt.second + utc_dt.microsecond / 1e6 - second) < 1e-6