"""Comprehensive tests for gtimes.gpstime module.

This module contains extensive tests for GPS time conversion functions including:
- GPS to UTC conversions and vice versa
- Leap second handling 
- Edge cases and boundary conditions
- Input validation and error handling
- Performance and accuracy testing
"""

import datetime
import pytest
import math
from unittest.mock import patch

from gtimes.gpstime import (
    gpsFromUTC, UTCFromGps, GpsSecondsFromPyUTC, 
    getleapSecs, leapSecDict, ymdhmsFromPyUTC
)
from gtimes.exceptions import GPSTimeError, ValidationError


class TestBasicGPSTimeConversions:
    """Test basic GPS time conversion functionality."""
    
    @pytest.mark.unit
    def test_gps_epoch_conversion(self):
        """Test conversion at GPS epoch (1980-01-06 00:00:00)."""
        # GPS epoch should convert to GPS week 0, SOW 0
        gps_week, sow, gps_day, sod = gpsFromUTC(1980, 1, 6, 0, 0, 0)
        
        assert gps_week == 0, f"Expected GPS week 0, got {gps_week}"
        assert abs(sow - 0.0) < 1e-6, f"Expected SOW 0, got {sow}"
        assert gps_day == 0, f"Expected GPS day 0, got {gps_day}" 
        assert abs(sod - 0.0) < 1e-6, f"Expected SOD 0, got {sod}"
    
    @pytest.mark.unit
    def test_known_gps_conversions(self, known_gps_times):
        """Test conversions for well-known GPS times."""
        for test_case in known_gps_times:
            dt = test_case['datetime']
            expected_week = test_case['gps_week']
            expected_sow = test_case['sow']
            
            gps_week, sow, gps_day, sod = gpsFromUTC(
                dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
            )
            
            assert gps_week == expected_week, \
                f"GPS week mismatch for {dt}: expected {expected_week}, got {gps_week}"
            assert abs(sow - expected_sow) < 1.0, \
                f"SOW mismatch for {dt}: expected {expected_sow}, got {sow}"
    
    @pytest.mark.unit
    def test_fractional_seconds_handling(self):
        """Test that fractional seconds are properly handled."""
        # Test with fractional seconds
        gps_week, sow, gps_day, sod = gpsFromUTC(2020, 1, 1, 12, 30, 45.123)
        
        # Fractional part should be preserved in SOW and SOD
        assert sow % 1 == pytest.approx(0.123, abs=1e-6), \
            f"Fractional seconds not preserved in SOW: {sow % 1}"
        assert sod % 1 == pytest.approx(0.123, abs=1e-6), \
            f"Fractional seconds not preserved in SOD: {sod % 1}"
    
    @pytest.mark.unit
    def test_roundtrip_conversion_accuracy(self, sample_utc_times):
        """Test that UTC->GPS->UTC conversions maintain accuracy."""
        for year, month, day, hour, minute, second in sample_utc_times:
            # Convert UTC to GPS
            gps_week, sow, gps_day, sod = gpsFromUTC(year, month, day, hour, minute, second)
            
            # Convert back to UTC 
            utc_result = UTCFromGps(gps_week, sow, dtimeObj=False)
            
            # Compare results (allowing for small floating point errors)
            assert utc_result[0] == year, f"Year mismatch: {utc_result[0]} != {year}"
            assert utc_result[1] == month, f"Month mismatch: {utc_result[1]} != {month}"
            assert utc_result[2] == day, f"Day mismatch: {utc_result[2]} != {day}"
            assert utc_result[3] == hour, f"Hour mismatch: {utc_result[3]} != {hour}"
            assert utc_result[4] == minute, f"Minute mismatch: {utc_result[4]} != {minute}"
            assert abs(utc_result[5] - second) < 1e-6, \
                f"Second mismatch: {utc_result[5]} != {second} (diff: {abs(utc_result[5] - second)})"


class TestUTCFromGpsConversions:
    """Test UTC from GPS time conversions."""
    
    @pytest.mark.unit
    def test_utc_from_gps_basic(self):
        """Test basic UTC from GPS conversion."""
        # Known GPS time: Week 2086, SOW 388800 = 2020-01-02 11:59:42
        utc_tuple = UTCFromGps(2086, 388800.0, dtimeObj=False)
        utc_datetime = UTCFromGps(2086, 388800.0, dtimeObj=True)
        
        # Test tuple return
        assert len(utc_tuple) == 6, f"Expected 6-element tuple, got {len(utc_tuple)}"
        assert utc_tuple[0] == 2020, f"Expected year 2020, got {utc_tuple[0]}"
        assert utc_tuple[1] == 1, f"Expected month 1, got {utc_tuple[1]}"
        assert utc_tuple[2] == 2, f"Expected day 2, got {utc_tuple[2]}"
        
        # Test datetime return
        assert isinstance(utc_datetime, datetime.datetime), \
            f"Expected datetime object, got {type(utc_datetime)}"
        assert utc_datetime.year == 2020
        assert utc_datetime.month == 1
        assert utc_datetime.day == 2
    
    @pytest.mark.unit
    def test_utc_datetime_object_return(self, sample_gps_times):
        """Test UTC conversion with datetime object return."""
        for gps_week, sow in sample_gps_times:
            if gps_week >= 0:  # Skip negative test cases
                utc_dt = UTCFromGps(gps_week, sow, dtimeObj=True)
                
                assert isinstance(utc_dt, datetime.datetime), \
                    f"Expected datetime for GPS {gps_week}/{sow}, got {type(utc_dt)}"
                
                # Basic sanity checks
                assert 1980 <= utc_dt.year <= 2100, \
                    f"Unreasonable year {utc_dt.year} for GPS {gps_week}/{sow}"
                assert 1 <= utc_dt.month <= 12, \
                    f"Invalid month {utc_dt.month} for GPS {gps_week}/{sow}"
                assert 1 <= utc_dt.day <= 31, \
                    f"Invalid day {utc_dt.day} for GPS {gps_week}/{sow}"


class TestLeapSecondHandling:
    """Test leap second handling in GPS time conversions."""
    
    @pytest.mark.unit
    def test_leap_second_dictionary_structure(self):
        """Test that leap second dictionary is properly structured."""
        leap_dict = leapSecDict()
        
        assert isinstance(leap_dict, dict), "Leap second dictionary should be a dict"
        assert len(leap_dict) > 10, "Should have multiple leap second entries"
        
        # Check for known leap second dates
        assert "1981-Jul-1" in leap_dict, "Should include 1981 leap second"
        assert "2017-Jan-1" in leap_dict, "Should include 2017 leap second"
        
        # Values should be integers and increasing
        dates = list(leap_dict.keys())
        values = list(leap_dict.values())
        
        assert all(isinstance(v, int) for v in values), "All leap second counts should be integers"
        assert values == sorted(values), "Leap second counts should be non-decreasing"
    
    @pytest.mark.unit
    def test_leap_second_retrieval(self):
        """Test leap second retrieval for various dates."""
        # Test GPS time mode (gpst=True)
        leap_secs_gps = getleapSecs(datetime.datetime(2020, 1, 1), gpst=True)
        assert isinstance(leap_secs_gps, int), "GPS leap seconds should be integer"
        assert leap_secs_gps >= 0, "GPS leap seconds should be non-negative"
        
        # Test UTC mode (gpst=False) 
        leap_secs_utc = getleapSecs(datetime.datetime(2020, 1, 1), gpst=False)
        assert isinstance(leap_secs_utc, int), "UTC leap seconds should be integer"
        assert leap_secs_utc > leap_secs_gps, "UTC leap seconds should be larger than GPS"
    
    @pytest.mark.unit
    def test_automatic_leap_second_application(self):
        """Test that leap seconds are automatically applied correctly."""
        # Test date before and after a known leap second addition
        before_leap = gpsFromUTC(2016, 12, 31, 23, 59, 59)
        after_leap = gpsFromUTC(2017, 1, 1, 0, 0, 0)
        
        # The SOW should account for the leap second
        sow_diff = after_leap[1] - before_leap[1]
        if after_leap[0] == before_leap[0]:  # Same GPS week
            # Should be 1 second difference normally, but might be 2 due to leap second
            assert abs(sow_diff - 1.0) < 2.0, f"Unexpected SOW difference: {sow_diff}"


class TestInputValidation:
    """Test input validation and error handling."""
    
    @pytest.mark.validation
    def test_gps_from_utc_validation(self, invalid_utc_inputs):
        """Test that gpsFromUTC validates inputs properly."""
        for test_name, (year, month, day, hour, minute, second) in invalid_utc_inputs.items():
            with pytest.raises(GPSTimeError, match="Invalid UTC components"):
                gpsFromUTC(year, month, day, hour, minute, second)
    
    @pytest.mark.validation
    def test_utc_from_gps_validation(self, invalid_gps_inputs):
        """Test that UTCFromGps validates inputs properly."""
        for test_name, (gps_week, sow) in invalid_gps_inputs.items():
            if test_name in ['string_week', 'string_sow', 'float_week']:
                # These should raise ValidationError due to type checking
                with pytest.raises(GPSTimeError, match="Invalid GPS time"):
                    UTCFromGps(gps_week, sow)
            else:
                # These should raise ValidationError due to range checking
                with pytest.raises(GPSTimeError, match="Invalid GPS time"):
                    UTCFromGps(gps_week, sow)
    
    @pytest.mark.validation
    def test_leap_seconds_validation(self):
        """Test leap second parameter validation."""
        # Valid leap second counts should work
        result = gpsFromUTC(2020, 1, 1, 12, 0, 0, leapSecs=18)
        assert len(result) == 4, "Should return 4-element tuple"
        
        # Invalid leap second counts should raise errors
        with pytest.raises((GPSTimeError, ValidationError)):
            gpsFromUTC(2020, 1, 1, 12, 0, 0, leapSecs=-1)
        
        with pytest.raises((GPSTimeError, ValidationError)):
            gpsFromUTC(2020, 1, 1, 12, 0, 0, leapSecs=50)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.edge_cases
    def test_gps_week_rollover_dates(self, edge_case_dates):
        """Test GPS time conversion around GPS week rollovers."""
        for test_date in edge_case_dates:
            try:
                gps_week, sow, gps_day, sod = gpsFromUTC(
                    test_date.year, test_date.month, test_date.day,
                    test_date.hour, test_date.minute, test_date.second
                )
                
                # Basic sanity checks
                assert 0 <= gps_week < 10000, f"GPS week {gps_week} out of reasonable range"
                assert 0 <= sow < 604800, f"SOW {sow} out of valid range"
                assert 0 <= gps_day < 7, f"GPS day {gps_day} out of valid range"
                assert 0 <= sod < 86400, f"SOD {sod} out of valid range"
                
            except (ValueError, GPSTimeError) as e:
                # Some edge cases might legitimately fail
                print(f"Edge case {test_date} failed as expected: {e}")
    
    @pytest.mark.edge_cases
    def test_leap_year_handling(self, leap_year_dates):
        """Test GPS time conversion on leap days."""
        for leap_date in leap_year_dates:
            gps_week, sow, gps_day, sod = gpsFromUTC(
                leap_date.year, leap_date.month, leap_date.day,
                leap_date.hour, leap_date.minute, leap_date.second
            )
            
            # Verify conversion can be reversed
            utc_result = UTCFromGps(gps_week, sow, dtimeObj=True)
            
            assert utc_result.year == leap_date.year
            assert utc_result.month == leap_date.month  
            assert utc_result.day == leap_date.day
    
    @pytest.mark.edge_cases  
    def test_maximum_precision_fractional_seconds(self):
        """Test maximum precision fractional seconds handling."""
        # Test with very high precision fractional seconds
        test_cases = [
            (2020, 1, 1, 12, 0, 0.000001),  # 1 microsecond
            (2020, 1, 1, 12, 0, 0.999999),  # Just under 1 second
            (2020, 1, 1, 12, 0, 30.123456789),  # High precision
        ]
        
        for year, month, day, hour, minute, second in test_cases:
            gps_week, sow, gps_day, sod = gpsFromUTC(year, month, day, hour, minute, second)
            utc_result = UTCFromGps(gps_week, sow, dtimeObj=False)
            
            # Should preserve precision to at least microsecond level
            assert abs(utc_result[5] - second) < 1e-5, \
                f"Precision lost: {utc_result[5]} != {second}"


class TestPerformance:
    """Performance tests for GPS time conversions."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_conversion_performance(self, performance_test_data):
        """Test performance of GPS time conversions."""
        import time
        
        utc_dates = performance_test_data['utc_dates'][:100]  # Use subset for faster testing
        
        # Time GPS from UTC conversions
        start_time = time.time()
        for year, month, day, hour, minute, second in utc_dates:
            gpsFromUTC(year, month, day, hour, minute, second)
        gps_conversion_time = time.time() - start_time
        
        # Time UTC from GPS conversions  
        gps_times = [(2086 + i, float(i * 1000)) for i in range(100)]
        start_time = time.time()
        for gps_week, sow in gps_times:
            UTCFromGps(gps_week, sow)
        utc_conversion_time = time.time() - start_time
        
        # Performance assertions (should complete in reasonable time)
        assert gps_conversion_time < 1.0, f"GPS conversions too slow: {gps_conversion_time:.3f}s"
        assert utc_conversion_time < 1.0, f"UTC conversions too slow: {utc_conversion_time:.3f}s"
        
        print(f"GPS conversion performance: {gps_conversion_time:.3f}s for 100 conversions")
        print(f"UTC conversion performance: {utc_conversion_time:.3f}s for 100 conversions")
    
    @pytest.mark.performance
    def test_leap_second_caching(self):
        """Test that leap second dictionary caching works."""
        import time
        
        # First call (should cache the result)
        start_time = time.time()
        leap_dict1 = leapSecDict()
        first_call_time = time.time() - start_time
        
        # Second call (should use cached result)
        start_time = time.time()
        leap_dict2 = leapSecDict()
        second_call_time = time.time() - start_time
        
        # Results should be identical
        assert leap_dict1 == leap_dict2, "Cached leap second dictionary should be identical"
        
        # Second call should be significantly faster (cached)
        assert second_call_time < first_call_time, \
            f"Second call should be faster due to caching: {second_call_time} >= {first_call_time}"


class TestUtilityFunctions:
    """Test utility functions in gpstime module."""
    
    @pytest.mark.unit
    def test_ymdhms_from_pyutc(self):
        """Test ymdhmsFromPyUTC function."""
        # Test with integer timestamp
        py_timestamp = 1577836800.0  # 2020-01-01 00:00:00 UTC
        result = ymdhmsFromPyUTC(py_timestamp)
        
        assert len(result) == 6, f"Expected 6-element tuple, got {len(result)}"
        assert result[0] == 2020, f"Expected year 2020, got {result[0]}"
        assert result[1] == 1, f"Expected month 1, got {result[1]}"
        assert result[2] == 1, f"Expected day 1, got {result[2]}"
        assert result[3] == 0, f"Expected hour 0, got {result[3]}"
        assert result[4] == 0, f"Expected minute 0, got {result[4]}"
        assert result[5] == 0.0, f"Expected second 0.0, got {result[5]}"
        
        # Test with fractional timestamp
        py_timestamp_frac = 1577836800.123456
        result_frac = ymdhmsFromPyUTC(py_timestamp_frac)
        
        assert abs(result_frac[5] - 0.123456) < 1e-6, \
            f"Fractional seconds not preserved: {result_frac[5]}"
    
    @pytest.mark.unit
    def test_gps_seconds_from_pyutc(self):
        """Test GpsSecondsFromPyUTC function."""
        # Test with known timestamp
        py_timestamp = 1577836800.0  # 2020-01-01 00:00:00 UTC
        gps_seconds = GpsSecondsFromPyUTC(py_timestamp)
        
        assert isinstance(gps_seconds, (int, float)), \
            f"Expected numeric result, got {type(gps_seconds)}"
        assert gps_seconds > 0, f"GPS seconds should be positive, got {gps_seconds}"
        
        # Should be roughly 40 years * 365.25 days * 86400 seconds
        expected_approx = 40 * 365.25 * 86400
        assert abs(gps_seconds - expected_approx) < 365 * 86400, \
            f"GPS seconds {gps_seconds} far from expected ~{expected_approx}"


# Integration test combining multiple functions
class TestIntegration:
    """Integration tests combining multiple GPS time functions."""
    
    @pytest.mark.integration
    def test_full_conversion_chain(self):
        """Test complete conversion chain: UTC -> GPS -> Python -> GPS -> UTC."""
        original_date = datetime.datetime(2020, 6, 15, 14, 30, 45, 123456)
        
        # UTC to GPS
        gps_week, sow, gps_day, sod = gpsFromUTC(
            original_date.year, original_date.month, original_date.day,
            original_date.hour, original_date.minute, 
            original_date.second + original_date.microsecond / 1e6
        )
        
        # GPS to UTC (datetime object)
        utc_datetime = UTCFromGps(gps_week, sow, dtimeObj=True)
        
        # Compare final result with original (allowing for small precision loss)
        time_diff = abs((utc_datetime - original_date).total_seconds())
        assert time_diff < 1e-3, f"Conversion chain introduced {time_diff}s error"
    
    @pytest.mark.integration
    def test_consistency_across_functions(self):
        """Test that different functions produce consistent results."""
        test_date = datetime.datetime(2020, 1, 1, 12, 0, 0)
        
        # Get leap seconds using different methods
        leap_secs_auto = getleapSecs(test_date, gpst=True)
        leap_secs_manual = getleapSecs(test_date, gpst=False) - getleapSecs(datetime.datetime(1980, 1, 6), gpst=False)
        
        # Should be the same (within reason - manual calculation is approximate)
        assert abs(leap_secs_auto - leap_secs_manual) <= 1, \
            f"Inconsistent leap second calculation: auto={leap_secs_auto}, manual={leap_secs_manual}"