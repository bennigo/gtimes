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


# RINEX filename tests
from gtimes.timefunc import (
    rinex2_filename,
    rinex3_filename,
    parse_rinex2_filename,
    parse_rinex3_filename,
    rinex_filename,
    convert_rinex_filename,
)


class TestRinex2Filename:
    """Test RINEX 2 short format filename generation."""

    def test_basic_daily_filename(self):
        """Test basic daily RINEX 2 filename."""
        dt = datetime.datetime(2026, 1, 15)
        name = rinex2_filename("ELDC", dt)
        assert name == "ELDC0150.26o"

    def test_hourly_filename_with_session(self):
        """Test hourly RINEX 2 filename with session letter."""
        dt = datetime.datetime(2026, 1, 15, 10, 0)
        name = rinex2_filename("ELDC", dt, session="k")
        assert name == "ELDC015k.26o"

    def test_navigation_file_type(self):
        """Test navigation file type."""
        dt = datetime.datetime(2026, 1, 15)
        name = rinex2_filename("ELDC", dt, file_type="n")
        assert name.endswith("n")
        assert "015" in name

    def test_station_uppercase(self):
        """Test station ID is always uppercase."""
        dt = datetime.datetime(2026, 1, 15)
        name = rinex2_filename("eldc", dt)
        assert name.startswith("ELDC")

    def test_station_truncation(self):
        """Test long station ID is truncated."""
        dt = datetime.datetime(2026, 1, 15)
        name = rinex2_filename("ABCDEFGH", dt)
        assert name.startswith("ABCD")

    def test_rinex3_type_mapping(self):
        """Test RINEX 3 file types are mapped to RINEX 2."""
        dt = datetime.datetime(2026, 1, 15)
        name = rinex2_filename("ELDC", dt, file_type="MO")
        assert name.endswith("o")  # Mixed Observation -> o


class TestRinex3Filename:
    """Test RINEX 3 long format filename generation."""

    def test_basic_daily_filename(self):
        """Test basic daily RINEX 3 filename."""
        dt = datetime.datetime(2026, 1, 15)
        name = rinex3_filename("ELDC", dt)
        assert name == "eldc00ISL_R_20260150000_01D_15S_MO.rnx"

    def test_hourly_filename(self):
        """Test hourly RINEX 3 filename."""
        dt = datetime.datetime(2026, 1, 15, 10, 0)
        name = rinex3_filename("ELDC", dt, file_period="01H", data_frequency="01S")
        assert "1000" in name  # Hour and minute
        assert "_01H_" in name
        assert "_01S_" in name

    def test_station_lowercase(self):
        """Test station ID is lowercase for RINEX 3."""
        dt = datetime.datetime(2026, 1, 15)
        name = rinex3_filename("ELDC", dt)
        assert name.startswith("eldc")

    def test_custom_country_code(self):
        """Test custom country code."""
        dt = datetime.datetime(2026, 1, 15)
        name = rinex3_filename("ELDC", dt, country_code="NOR")
        assert "00NOR_" in name

    def test_custom_data_source(self):
        """Test custom data source."""
        dt = datetime.datetime(2026, 1, 15)
        name = rinex3_filename("ELDC", dt, data_source="S")
        assert "_S_" in name

    def test_extension(self):
        """Test .rnx extension."""
        dt = datetime.datetime(2026, 1, 15)
        name = rinex3_filename("ELDC", dt)
        assert name.endswith(".rnx")


class TestParseRinex2Filename:
    """Test RINEX 2 filename parsing."""

    def test_parse_daily_file(self):
        """Test parsing daily RINEX 2 file."""
        parsed = parse_rinex2_filename("ELDC0150.26o")
        assert parsed is not None
        assert parsed["station"] == "ELDC"
        assert parsed["doy"] == 15
        assert parsed["year"] == 2026
        assert parsed["file_type"] == "o"
        assert parsed["session"] == "0"

    def test_parse_hourly_file(self):
        """Test parsing hourly RINEX 2 file."""
        parsed = parse_rinex2_filename("ELDC015k.26o")
        assert parsed is not None
        assert parsed["session"] == "k"
        assert parsed["datetime"].hour == 10  # k = hour 10

    def test_parse_old_year(self):
        """Test parsing file from 1990s."""
        parsed = parse_rinex2_filename("ELDC0150.99o")
        assert parsed is not None
        assert parsed["year"] == 1999

    def test_invalid_filename(self):
        """Test parsing invalid filename returns None."""
        parsed = parse_rinex2_filename("invalid.txt")
        assert parsed is None


class TestParseRinex3Filename:
    """Test RINEX 3 filename parsing."""

    def test_parse_daily_file(self):
        """Test parsing daily RINEX 3 file."""
        parsed = parse_rinex3_filename("eldc00ISL_R_20260150000_01D_15S_MO.rnx")
        assert parsed is not None
        assert parsed["station"] == "ELDC"
        assert parsed["year"] == 2026
        assert parsed["doy"] == 15
        assert parsed["file_period"] == "01D"
        assert parsed["file_type"] == "MO"

    def test_parse_hourly_file(self):
        """Test parsing hourly RINEX 3 file."""
        parsed = parse_rinex3_filename("eldc00ISL_R_20260151000_01H_01S_MO.rnx")
        assert parsed is not None
        assert parsed["hour"] == 10
        assert parsed["minute"] == 0
        assert parsed["file_period"] == "01H"

    def test_parse_country_code(self):
        """Test country code parsing."""
        parsed = parse_rinex3_filename("eldc00NOR_R_20260150000_01D_15S_MO.rnx")
        assert parsed is not None
        assert parsed["country_code"] == "NOR"

    def test_invalid_filename(self):
        """Test parsing invalid filename returns None."""
        parsed = parse_rinex3_filename("invalid.txt")
        assert parsed is None


class TestConvertRinexFilename:
    """Test RINEX filename conversion between versions."""

    def test_v2_to_v3(self):
        """Test conversion from RINEX 2 to RINEX 3."""
        result = convert_rinex_filename("ELDC0150.26o", 3)
        assert result is not None
        assert result.startswith("eldc")
        assert "_R_" in result
        assert "2026015" in result
        assert result.endswith(".rnx")

    def test_v3_to_v2(self):
        """Test conversion from RINEX 3 to RINEX 2."""
        result = convert_rinex_filename("eldc00ISL_R_20260151000_01H_01S_MO.rnx", 2)
        assert result is not None
        assert result.startswith("ELDC")
        assert "015" in result
        assert result.endswith("o")

    def test_v3_to_v2_hourly(self):
        """Test hourly file conversion preserves session letter."""
        result = convert_rinex_filename("eldc00ISL_R_20260151000_01H_01S_MO.rnx", 2)
        assert result is not None
        # Hour 10 should map to session 'k'
        assert "015k" in result

    def test_invalid_filename(self):
        """Test conversion of invalid filename returns None."""
        result = convert_rinex_filename("invalid.txt", 3)
        assert result is None


class TestRinexFilenameUnified:
    """Test unified rinex_filename function."""

    def test_version_2(self):
        """Test generating RINEX 2 filename."""
        dt = datetime.datetime(2026, 1, 15)
        name = rinex_filename("ELDC", dt, version=2)
        assert name == "ELDC0150.26o"

    def test_version_3(self):
        """Test generating RINEX 3 filename."""
        dt = datetime.datetime(2026, 1, 15)
        name = rinex_filename("ELDC", dt, version=3)
        assert name.startswith("eldc")
        assert name.endswith(".rnx")

    def test_hourly_frequency(self):
        """Test hourly file generation."""
        dt = datetime.datetime(2026, 1, 15, 10, 0)
        name_v2 = rinex_filename("ELDC", dt, version=2, frequency="1H")
        assert "015" in name_v2
        # Should have hour letter 'k' for hour 10
        assert "k" in name_v2


# Time-range utility tests (migrated from receivers.utils.time_utils)
from gtimes.timefunc import (
    previous_complete_period,
    generate_time_range,
    generate_datetime_list,
    generate_period_ranges,
)


class TestPreviousCompletePeriod:
    """Alignment of the previous-complete-period boundary."""

    def test_hourly_aligns_to_current_hour(self):
        ref = datetime.datetime(2026, 4, 17, 22, 41, tzinfo=datetime.timezone.utc)
        aligned = previous_complete_period("1H", now=ref)
        assert aligned == datetime.datetime(2026, 4, 17, 22, 0, tzinfo=datetime.timezone.utc)

    def test_daily_aligns_to_midnight(self):
        ref = datetime.datetime(2026, 4, 17, 22, 41, tzinfo=datetime.timezone.utc)
        aligned = previous_complete_period("1D", now=ref)
        assert aligned == datetime.datetime(2026, 4, 17, 0, 0, tzinfo=datetime.timezone.utc)

    def test_timedelta_input_equivalent_to_string(self):
        ref = datetime.datetime(2026, 4, 17, 22, 41, tzinfo=datetime.timezone.utc)
        via_str = previous_complete_period("1H", now=ref)
        via_td = previous_complete_period(datetime.timedelta(hours=1), now=ref)
        assert via_str == via_td

    def test_sub_hour_truncates_to_period_multiple(self):
        ref = datetime.datetime(2026, 4, 17, 22, 41, tzinfo=datetime.timezone.utc)
        aligned = previous_complete_period(datetime.timedelta(minutes=15), now=ref)
        # 22:41 → 22:30 (3 * 15m past 22:00 is 22:45, so 22:30 is the last complete mark)
        assert aligned == datetime.datetime(2026, 4, 17, 22, 30, tzinfo=datetime.timezone.utc)


class TestGenerateTimeRange:
    """End-exclusive lookback window."""

    def test_hourly_24(self):
        ref = datetime.datetime(2026, 4, 17, 22, 41, tzinfo=datetime.timezone.utc)
        start, end = generate_time_range("1H", 24, now=ref)
        assert end == datetime.datetime(2026, 4, 17, 22, 0, tzinfo=datetime.timezone.utc)
        assert start == datetime.datetime(2026, 4, 16, 22, 0, tzinfo=datetime.timezone.utc)
        assert (end - start) == datetime.timedelta(hours=24)

    def test_daily_7(self):
        ref = datetime.datetime(2026, 4, 17, 22, 41, tzinfo=datetime.timezone.utc)
        start, end = generate_time_range("1D", 7, now=ref)
        assert end == datetime.datetime(2026, 4, 17, tzinfo=datetime.timezone.utc)
        assert start == datetime.datetime(2026, 4, 10, tzinfo=datetime.timezone.utc)


class TestGenerateDatetimeList:
    """Inclusive-start, exclusive-end datetime iteration."""

    def test_daily_spans_three_days(self):
        a = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        b = datetime.datetime(2026, 1, 4, tzinfo=datetime.timezone.utc)
        dts = generate_datetime_list(a, b, "1D")
        assert [d.day for d in dts] == [1, 2, 3]

    def test_reverse_is_newest_first(self):
        a = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        b = datetime.datetime(2026, 1, 4, tzinfo=datetime.timezone.utc)
        dts = generate_datetime_list(a, b, "1D", reverse=True)
        assert [d.day for d in dts] == [3, 2, 1]

    def test_empty_when_start_ge_end(self):
        a = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        assert generate_datetime_list(a, a, "1H") == []


class TestGeneratePeriodRanges:
    """Sub-range tuples covering the interval."""

    def test_clamps_last_range(self):
        a = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        b = datetime.datetime(2026, 1, 3, 12, tzinfo=datetime.timezone.utc)  # 2.5 days
        ranges = generate_period_ranges(a, b, "1D")
        # Three tuples: (1,2), (2,3), (3,3 12h) — last clamped
        assert len(ranges) == 3
        assert ranges[-1][1] == b

    def test_reverse_flips_order(self):
        a = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        b = datetime.datetime(2026, 1, 4, tzinfo=datetime.timezone.utc)
        ranges = generate_period_ranges(a, b, "1D", reverse=True)
        assert [s.day for s, _ in ranges] == [3, 2, 1]


from gtimes.timefunc import parse_datetime_flexible


class TestParseDatetimeFlexible:
    """Multi-format datetime string parsing."""

    def test_datetime_passthrough(self):
        dt = datetime.datetime(2026, 4, 17, 14, 30)
        assert parse_datetime_flexible(dt) is dt

    def test_iso_format(self):
        assert parse_datetime_flexible("2026-04-17T14:30:00") == datetime.datetime(
            2026, 4, 17, 14, 30
        )

    def test_date_only(self):
        assert parse_datetime_flexible("2026-04-17") == datetime.datetime(2026, 4, 17)

    def test_compact_date(self):
        assert parse_datetime_flexible("20260417") == datetime.datetime(2026, 4, 17)

    def test_compact_with_dash(self):
        assert parse_datetime_flexible("20260417-1430") == datetime.datetime(
            2026, 4, 17, 14, 30
        )

    def test_standard_format(self):
        assert parse_datetime_flexible("2026-04-17 14:30:00") == datetime.datetime(
            2026, 4, 17, 14, 30
        )

    def test_extra_format_takes_priority_over_builtin(self):
        result = parse_datetime_flexible("17/04/2026", extra_formats=["%d/%m/%Y"])
        assert result == datetime.datetime(2026, 4, 17)

    def test_invalid_raises_value_error(self):
        with pytest.raises(ValueError, match="Could not parse"):
            parse_datetime_flexible("not-a-date")