"""Comprehensive tests for gtimes.timefunc module.

This module contains extensive tests for time utility functions including:
- Fractional year conversions
- Date and time formatting
- Time shifting and date arithmetic
- Date path generation for file workflows
- GPS time utilities
"""

import datetime
import pytest
import math
from unittest.mock import patch

from gtimes.timefunc import (
    TimefromYearf, currYearfDate, dTimetoYearf, shifTime,
    currDatetime, currDate, datepathlist, shlyear, DaysinYear,
    hourABC, gpsWeekDay, gpsfDateTime, dateTuple, round_to_hour
)
from gtimes.exceptions import FractionalYearError, ValidationError


class TestFractionalYearConversions:
    """Test fractional year conversion functions."""
    
    @pytest.mark.unit
    def test_time_from_yearf_basic(self):
        """Test basic fractional year to datetime conversion."""
        # Test exact year boundaries
        dt_2020 = TimefromYearf(2020.0)
        assert dt_2020.year == 2020
        assert dt_2020.month == 1
        assert dt_2020.day == 1
        assert dt_2020.hour == 0
        assert dt_2020.minute == 0
        
        # Test mid-year (approximately July 2nd)
        dt_mid = TimefromYearf(2020.5)
        assert dt_mid.year == 2020
        assert dt_mid.month >= 6  # Should be in summer
        assert dt_mid.month <= 7
    
    @pytest.mark.unit
    def test_time_from_yearf_with_string_formatting(self, sample_fractional_years):
        """Test fractional year conversion with string output."""
        for yearf in sample_fractional_years[:3]:  # Test first 3 to avoid long test
            if yearf >= 1980.0:  # Valid range
                # Test various format strings
                date_str = TimefromYearf(yearf, String="%Y-%m-%d")
                assert len(date_str) == 10, f"Expected YYYY-MM-DD format, got {date_str}"
                assert date_str.count('-') == 2, f"Expected 2 dashes, got {date_str}"
                
                # Test time format
                datetime_str = TimefromYearf(yearf, String="%Y-%m-%d %H:%M:%S")
                assert len(datetime_str) >= 19, f"Expected datetime format, got {datetime_str}"
                
                # Test ordinal format
                ordinal = TimefromYearf(yearf, String="ordinalf")
                assert isinstance(ordinal, float), f"Expected float for ordinal, got {type(ordinal)}"
    
    @pytest.mark.unit
    def test_time_from_yearf_hour_rounding(self):
        """Test hour rounding functionality."""
        # Test fractional year that results in non-zero minutes
        yearf_with_minutes = 2020.12345  # Should have some fractional hour component
        
        dt_normal = TimefromYearf(yearf_with_minutes, rhour=False)
        dt_rounded = TimefromYearf(yearf_with_minutes, rhour=True)
        
        # Rounded version should have minute = 0 or 30 (depending on implementation)
        assert dt_rounded.minute in [0, 30], \
            f"Hour rounding should result in 0 or 30 minutes, got {dt_rounded.minute}"
    
    @pytest.mark.unit
    def test_dtime_to_yearf(self):
        """Test datetime to fractional year conversion."""
        test_dates = [
            datetime.datetime(2020, 1, 1, 0, 0, 0),    # Start of year
            datetime.datetime(2020, 7, 1, 12, 0, 0),   # Mid year
            datetime.datetime(2020, 12, 31, 23, 59, 59), # End of year
        ]
        
        for test_date in test_dates:
            yearf = dTimetoYearf(test_date)
            
            # Basic checks
            assert isinstance(yearf, float), f"Expected float, got {type(yearf)}"
            assert yearf >= test_date.year, f"Fractional year {yearf} should be >= {test_date.year}"
            assert yearf < test_date.year + 1, f"Fractional year {yearf} should be < {test_date.year + 1}"
            
            # Test roundtrip conversion
            dt_back = TimefromYearf(yearf)
            time_diff = abs((dt_back - test_date).total_seconds())
            assert time_diff < 60, f"Roundtrip error too large: {time_diff} seconds"
    
    @pytest.mark.unit
    def test_curr_yearf_date(self):
        """Test current fractional year calculation."""
        yearf_now = currYearfDate()
        current_year = datetime.datetime.now().year
        
        assert isinstance(yearf_now, float), f"Expected float, got {type(yearf_now)}"
        assert current_year <= yearf_now < current_year + 1, \
            f"Current fractional year {yearf_now} outside expected range [{current_year}, {current_year + 1})"
    
    @pytest.mark.validation
    def test_fractional_year_validation(self):
        """Test fractional year input validation."""
        # Valid fractional years should work
        valid_years = [1980.0, 2020.5, 2023.99]
        for yearf in valid_years:
            result = TimefromYearf(yearf)
            assert isinstance(result, datetime.datetime), \
                f"Valid year {yearf} should return datetime"
        
        # Invalid fractional years should raise errors
        invalid_years = [1900.0, 2200.0, "invalid"]
        for yearf in invalid_years:
            with pytest.raises(FractionalYearError):
                TimefromYearf(yearf)


class TestTimeShiftingAndArithmetic:
    """Test time shifting and date arithmetic functions."""
    
    @pytest.mark.unit
    def test_shift_time_parsing(self):
        """Test time shift string parsing."""
        # Test basic day shift
        shift_dict = shifTime("d5")
        assert shift_dict == {"days": 5}, f"Expected days: 5, got {shift_dict}"
        
        # Test negative shift
        shift_dict = shifTime("d-3")
        assert shift_dict == {"days": -3}, f"Expected days: -3, got {shift_dict}"
        
        # Test multiple components
        shift_dict = shifTime("d1:H12:M30")
        expected = {"days": 1, "hours": 12, "minutes": 30}
        assert shift_dict == expected, f"Expected {expected}, got {shift_dict}"
        
        # Test seconds and microseconds
        shift_dict = shifTime("S30:f500000")
        expected = {"seconds": 30, "microseconds": 500000}
        assert shift_dict == expected, f"Expected {expected}, got {shift_dict}"
    
    @pytest.mark.unit
    def test_curr_datetime_with_shifts(self):
        """Test current datetime calculation with shifts."""
        base_date = datetime.datetime(2020, 6, 15, 12, 0, 0)
        
        # Test day shift
        shifted_date = currDatetime(days="d5", refday=base_date)
        expected_date = base_date + datetime.timedelta(days=5)
        assert shifted_date == expected_date, \
            f"Expected {expected_date}, got {shifted_date}"
        
        # Test negative shift
        shifted_date = currDatetime(days="d-10", refday=base_date)
        expected_date = base_date + datetime.timedelta(days=-10)
        assert shifted_date == expected_date, \
            f"Expected {expected_date}, got {shifted_date}"
        
        # Test string formatting
        date_str = currDatetime(days="d0", refday=base_date, String="%Y-%m-%d")
        expected_str = base_date.strftime("%Y-%m-%d")
        assert date_str == expected_str, \
            f"Expected {expected_str}, got {date_str}"
    
    @pytest.mark.unit
    def test_curr_date_functionality(self):
        """Test current date calculation functionality."""
        base_date = datetime.date(2020, 6, 15)
        
        # Test basic date shift
        shifted_date = currDate(days=5, refday=base_date)
        expected_date = base_date + datetime.timedelta(days=5)
        assert shifted_date == expected_date, \
            f"Expected {expected_date}, got {shifted_date}"
        
        # Test with string output
        date_str = currDate(days=0, refday=base_date, String="%Y%m%d")
        expected_str = base_date.strftime("%Y%m%d")
        assert date_str == expected_str, \
            f"Expected {expected_str}, got {date_str}"
        
        # Test fractional year input
        yearf_date = currDate(days=0, refday=2020.5, fromYearf=True)
        assert isinstance(yearf_date, datetime.date), \
            f"Expected date object, got {type(yearf_date)}"


class TestDatePathGeneration:
    """Test date path generation for file workflows."""
    
    @pytest.mark.unit
    def test_datepathlist_basic(self):
        """Test basic date path list generation."""
        start_date = datetime.datetime(2020, 1, 1)
        end_date = datetime.datetime(2020, 1, 3)
        
        # Test basic daily pattern
        pattern = "data_%Y%m%d.txt"
        paths = datepathlist(pattern, "1D", start_date, end_date)
        
        assert isinstance(paths, list), f"Expected list, got {type(paths)}"
        assert len(paths) >= 2, f"Expected at least 2 paths, got {len(paths)}"
        
        # Check that paths contain expected dates
        paths_str = ' '.join(paths)
        assert "20200101" in paths_str, "Should contain 2020-01-01"
        assert "20200102" in paths_str, "Should contain 2020-01-02"
    
    @pytest.mark.unit
    def test_datepathlist_gps_formatting(self):
        """Test GPS-specific formatting in date path generation."""
        start_date = datetime.datetime(2020, 1, 1)
        end_date = datetime.datetime(2020, 1, 3)
        
        # Test GPS week formatting
        pattern = "file_#gpsw_%Y%m%d.dat"
        paths = datepathlist(pattern, "1D", start_date, end_date)
        
        # Should replace #gpsw with GPS week number
        paths_str = ' '.join(paths)
        assert "#gpsw" not in paths_str, "Should replace #gpsw token"
        assert "2086" in paths_str or "2087" in paths_str, "Should contain GPS week number"
    
    @pytest.mark.unit
    def test_datepathlist_rinex_formatting(self):
        """Test RINEX filename formatting."""
        start_date = datetime.datetime(2020, 1, 1)
        end_date = datetime.datetime(2020, 1, 3)
        
        # Test RINEX 2 formatting
        pattern = "STATION#Rin2O.Z"
        paths = datepathlist(pattern, "1D", start_date, end_date)
        
        # Should replace #Rin2 with DOY + session + year
        paths_str = ' '.join(paths)
        assert "#Rin2" not in paths_str, "Should replace #Rin2 token"
        assert "20O.Z" in paths_str, "Should contain RINEX 2 format"
    
    @pytest.mark.unit  
    def test_datepathlist_month_formatting(self):
        """Test month abbreviation formatting."""
        start_date = datetime.datetime(2020, 3, 1)  # March
        end_date = datetime.datetime(2020, 3, 3)
        
        # Test month abbreviation
        pattern = "/data/2020/#b/file_%Y%m%d.dat"
        paths = datepathlist(pattern, "1D", start_date, end_date)
        
        # Should replace #b with lowercase month abbreviation
        paths_str = ' '.join(paths)
        assert "#b" not in paths_str, "Should replace #b token"
        assert "mar" in paths_str.lower(), "Should contain 'mar' for March"


class TestUtilityFunctions:
    """Test various utility functions."""
    
    @pytest.mark.unit
    def test_shlyear_conversion(self):
        """Test short/long year conversion."""
        # Test 4-digit to 2-digit
        short_year = shlyear(yyyy=2020, change=True)
        assert short_year == 20, f"Expected 20, got {short_year}"
        
        # Test 2-digit to 4-digit  
        long_year = shlyear(yyyy=20, change=True)
        assert long_year == 2020, f"Expected 2020, got {long_year}"
        
        # Test edge cases around century
        century_test = shlyear(yyyy=0, change=True)
        assert century_test == 2000, f"Expected 2000 for year 0, got {century_test}"
    
    @pytest.mark.unit
    def test_days_in_year(self):
        """Test days in year calculation."""
        # Test regular year
        days_2021 = DaysinYear(2021)
        assert days_2021 == 365, f"Expected 365 days in 2021, got {days_2021}"
        
        # Test leap year
        days_2020 = DaysinYear(2020)
        assert days_2020 == 366, f"Expected 366 days in 2020, got {days_2020}"
        
        # Test century non-leap year
        days_1900 = DaysinYear(1900)
        assert days_1900 == 365, f"Expected 365 days in 1900, got {days_1900}"
        
        # Test century leap year
        days_2000 = DaysinYear(2000)
        assert days_2000 == 366, f"Expected 366 days in 2000, got {days_2000}"
    
    @pytest.mark.unit
    def test_hour_abc_conversion(self):
        """Test hour to alphabetic conversion."""
        # Test basic hour conversions
        assert hourABC(0) == 'a', "Hour 0 should be 'a'"
        assert hourABC(1) == 'b', "Hour 1 should be 'b'"
        assert hourABC(23) == 'x', "Hour 23 should be 'x'"
        
        # Test invalid hours
        with pytest.raises((ValueError, IndexError)):
            hourABC(24)  # Invalid hour
        with pytest.raises((ValueError, IndexError)):
            hourABC(-1)  # Negative hour
    
    @pytest.mark.unit
    def test_gps_week_day_calculation(self):
        """Test GPS week and day calculation."""
        # Test known date
        test_date = datetime.datetime(2020, 1, 1, 12, 0, 0)
        gps_week, gps_day = gpsWeekDay(refday=test_date)
        
        assert isinstance(gps_week, int), f"GPS week should be int, got {type(gps_week)}"
        assert isinstance(gps_day, int), f"GPS day should be int, got {type(gps_day)}"
        assert 0 <= gps_day <= 6, f"GPS day should be 0-6, got {gps_day}"
        assert gps_week >= 0, f"GPS week should be non-negative, got {gps_week}"
    
    @pytest.mark.unit
    def test_gpsf_date_time(self):
        """Test GPS formatted date time."""
        test_date = datetime.datetime(2020, 6, 15, 14, 30, 45)
        gps_week, sow, dow, sod = gpsfDateTime(refday=test_date)
        
        # Verify types and ranges
        assert isinstance(gps_week, int), f"GPS week should be int, got {type(gps_week)}"
        assert isinstance(sow, (int, float)), f"SOW should be numeric, got {type(sow)}"
        assert isinstance(dow, int), f"DOW should be int, got {type(dow)}"
        assert isinstance(sod, (int, float)), f"SOD should be numeric, got {type(sod)}"
        
        # Verify ranges
        assert 0 <= dow <= 6, f"Day of week should be 0-6, got {dow}"
        assert 0 <= sod < 86400, f"Seconds of day should be 0-86399, got {sod}"
        assert 0 <= sow < 604800, f"Seconds of week should be 0-604799, got {sow}"
    
    @pytest.mark.unit
    def test_date_tuple_generation(self):
        """Test date tuple generation."""
        test_date = datetime.datetime(2020, 6, 15, 14, 30, 45)
        date_tuple = dateTuple(refday=test_date)
        
        # Should return tuple with multiple elements
        assert isinstance(date_tuple, tuple), f"Expected tuple, got {type(date_tuple)}"
        assert len(date_tuple) >= 8, f"Expected at least 8 elements, got {len(date_tuple)}"
        
        # Check some expected values
        assert date_tuple[0] == 2020, f"Expected year 2020, got {date_tuple[0]}"
        assert date_tuple[1] == 6, f"Expected month 6, got {date_tuple[1]}"
        assert date_tuple[2] == 15, f"Expected day 15, got {date_tuple[2]}"
    
    @pytest.mark.unit
    def test_round_to_hour(self):
        """Test hour rounding functionality."""
        # Test rounding down (minutes < 30)
        dt_down = datetime.datetime(2020, 1, 1, 12, 15, 30)
        rounded_down = round_to_hour(dt_down)
        assert rounded_down.hour == 12, f"Expected hour 12, got {rounded_down.hour}"
        assert rounded_down.minute == 0, f"Expected minute 0, got {rounded_down.minute}"
        assert rounded_down.second == 0, f"Expected second 0, got {rounded_down.second}"
        
        # Test rounding up (minutes >= 30)  
        dt_up = datetime.datetime(2020, 1, 1, 12, 45, 30)
        rounded_up = round_to_hour(dt_up)
        assert rounded_up.hour == 13, f"Expected hour 13, got {rounded_up.hour}"
        assert rounded_up.minute == 0, f"Expected minute 0, got {rounded_up.minute}"
        assert rounded_up.second == 0, f"Expected second 0, got {rounded_up.second}"
        
        # Test exact 30 minutes (should round up)
        dt_exact = datetime.datetime(2020, 1, 1, 12, 30, 0)
        rounded_exact = round_to_hour(dt_exact)
        assert rounded_exact.hour == 13, f"Expected hour 13, got {rounded_exact.hour}"


class TestPerformanceAndEdgeCases:
    """Test performance and edge cases for time functions."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_fractional_year_conversion_performance(self, sample_fractional_years):
        """Test performance of fractional year conversions."""
        import time
        
        # Test batch conversion performance
        start_time = time.time()
        for _ in range(100):
            for yearf in sample_fractional_years:
                if yearf >= 1980.0:  # Valid range only
                    TimefromYearf(yearf)
        conversion_time = time.time() - start_time
        
        # Should complete reasonably quickly
        assert conversion_time < 2.0, f"Conversions too slow: {conversion_time:.3f}s"
    
    @pytest.mark.edge_cases
    def test_leap_year_edge_cases(self):
        """Test fractional year conversion on leap years."""
        leap_years = [2000, 2004, 2020]  # Various leap years
        
        for year in leap_years:
            # Test Feb 29 specifically
            feb29 = datetime.datetime(year, 2, 29, 12, 0, 0)
            yearf = dTimetoYearf(feb29)
            
            # Convert back
            dt_back = TimefromYearf(yearf)
            
            # Should be very close to original
            time_diff = abs((dt_back - feb29).total_seconds())
            assert time_diff < 3600, f"Leap year conversion error too large: {time_diff} seconds"
    
    @pytest.mark.edge_cases
    def test_year_boundary_conversions(self):
        """Test conversions at year boundaries."""
        # Test start of year
        start_year = datetime.datetime(2020, 1, 1, 0, 0, 0)
        yearf_start = dTimetoYearf(start_year)
        assert abs(yearf_start - 2020.0) < 1e-6, \
            f"Start of year should be close to integer: {yearf_start}"
        
        # Test end of year  
        end_year = datetime.datetime(2020, 12, 31, 23, 59, 59)
        yearf_end = dTimetoYearf(end_year)
        assert yearf_end < 2021.0, f"End of year should be < next year: {yearf_end}"
        assert yearf_end > 2020.99, f"End of year should be close to 1.0: {yearf_end}"


class TestIntegrationScenarios:
    """Integration tests combining multiple functions."""
    
    @pytest.mark.integration  
    def test_rinex_filename_generation(self):
        """Test realistic RINEX filename generation workflow."""
        # Simulate generating RINEX filenames for a week of data
        start_date = datetime.datetime(2020, 6, 15, 0, 0, 0)
        end_date = datetime.datetime(2020, 6, 22, 0, 0, 0)
        
        # Generate daily RINEX observation files
        pattern = "REYK%j0.%yO"
        filenames = datepathlist(pattern, "1D", start_date, end_date)
        
        assert len(filenames) >= 7, f"Expected at least 7 daily files, got {len(filenames)}"
        
        # Check filename format
        for filename in filenames:
            assert filename.startswith("REYK"), f"Should start with station name: {filename}"
            assert filename.endswith("O"), f"Should end with observation type: {filename}"
            assert len(filename) == 12, f"RINEX filename should be 12 chars: {filename}"
    
    @pytest.mark.integration
    def test_gps_processing_workflow(self):
        """Test a realistic GPS data processing workflow."""
        # Start with a fractional year from GAMIT processing
        process_yearf = 2020.45  # Mid-year processing epoch
        
        # Convert to datetime for file organization
        process_dt = TimefromYearf(process_yearf)
        
        # Generate GPS week/day for processing organization
        gps_week, gps_day = gpsWeekDay(process_dt)
        
        # Create processing directory path
        proc_path = currDatetime(
            days=0, 
            refday=process_dt,
            String="/gps_proc/%Y/%j/week_%04d" % gps_week
        )
        
        # Verify workflow components
        assert isinstance(process_dt, datetime.datetime), "Should convert to datetime"
        assert isinstance(gps_week, int) and gps_week > 0, "Should have valid GPS week"
        assert isinstance(proc_path, str) and "gps_proc" in proc_path, "Should generate path"
        assert str(gps_week) in proc_path, "Path should contain GPS week"
    
    @pytest.mark.integration
    def test_time_series_analysis_workflow(self):
        """Test time series analysis workflow with fractional years."""
        # Simulate GAMIT time series with fractional years
        base_year = 2020.0
        time_series = [base_year + i/365.25 for i in range(0, 365, 30)]  # Monthly
        
        # Convert each fractional year to datetime
        datetime_series = []
        for yearf in time_series:
            dt = TimefromYearf(yearf)
            datetime_series.append(dt)
        
        # Verify time series properties
        assert len(datetime_series) == len(time_series), "Should preserve series length"
        
        # Check chronological order
        for i in range(1, len(datetime_series)):
            assert datetime_series[i] > datetime_series[i-1], \
                f"Time series should be chronological: {datetime_series[i-1]} >= {datetime_series[i]}"
        
        # Check span is approximately one year
        time_span = datetime_series[-1] - datetime_series[0]
        assert 300 < time_span.days < 400, \
            f"Time span should be ~1 year: {time_span.days} days"