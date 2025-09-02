"""Test validation and error handling improvements."""

import datetime
import pytest

from gtimes.exceptions import (
    GPSTimeError, ValidationError, FractionalYearError,
    validate_gps_week, validate_seconds_of_week, 
    validate_utc_components, validate_fractional_year
)
from gtimes.gpstime import gpsFromUTC, UTCFromGps
from gtimes.timefunc import TimefromYearf


class TestValidationFunctions:
    """Test individual validation functions."""

    def test_validate_gps_week_valid(self):
        """Test GPS week validation with valid values."""
        assert validate_gps_week(0) == 0
        assert validate_gps_week(1000) == 1000
        assert validate_gps_week(2086) == 2086

    def test_validate_gps_week_invalid(self):
        """Test GPS week validation with invalid values."""
        with pytest.raises(ValidationError, match="GPS week must be an integer"):
            validate_gps_week(1000.5)
        
        with pytest.raises(ValidationError, match="GPS week cannot be negative"):
            validate_gps_week(-1)
        
        with pytest.raises(ValidationError, match="GPS week is unreasonably large"):
            validate_gps_week(99999)

    def test_validate_sow_valid(self):
        """Test seconds of week validation with valid values."""
        assert validate_seconds_of_week(0) == 0.0
        assert validate_seconds_of_week(388800) == 388800.0
        assert validate_seconds_of_week(604799.999) == 604799.999

    def test_validate_sow_invalid(self):
        """Test seconds of week validation with invalid values."""
        with pytest.raises(ValidationError, match="Seconds of week must be numeric"):
            validate_seconds_of_week("invalid")
        
        with pytest.raises(ValidationError, match="Seconds of week cannot be negative"):
            validate_seconds_of_week(-1)
        
        with pytest.raises(ValidationError, match="Seconds of week must be less than 604800"):
            validate_seconds_of_week(604800)

    def test_validate_utc_components_valid(self):
        """Test UTC components validation with valid values."""
        result = validate_utc_components(2020, 1, 1, 12, 0, 0.0)
        assert result == (2020, 1, 1, 12, 0, 0.0)
        
        # Test with fractional seconds
        result = validate_utc_components(2020, 6, 15, 14, 30, 45.123)
        assert result == (2020, 6, 15, 14, 30, 45.123)

    def test_validate_utc_components_invalid(self):
        """Test UTC components validation with invalid values."""
        # Invalid year
        with pytest.raises(ValidationError, match="Year must be between 1980 and 2100"):
            validate_utc_components(1900, 1, 1, 12, 0, 0)
        
        # Invalid month
        with pytest.raises(ValidationError, match="Month must be between 1 and 12"):
            validate_utc_components(2020, 13, 1, 12, 0, 0)
        
        # Invalid day
        with pytest.raises(ValidationError, match="Day must be between 1 and 31"):
            validate_utc_components(2020, 1, 32, 12, 0, 0)
        
        # Invalid hour
        with pytest.raises(ValidationError, match="Hour must be between 0 and 23"):
            validate_utc_components(2020, 1, 1, 24, 0, 0)
        
        # Invalid minute
        with pytest.raises(ValidationError, match="Minute must be between 0 and 59"):
            validate_utc_components(2020, 1, 1, 12, 60, 0)
        
        # Invalid second
        with pytest.raises(ValidationError, match="Second must be between 0 and 59.999"):
            validate_utc_components(2020, 1, 1, 12, 0, 60.0)

    def test_validate_fractional_year_valid(self):
        """Test fractional year validation with valid values."""
        assert validate_fractional_year(2020.0) == 2020.0
        assert validate_fractional_year(2023.5) == 2023.5
        assert validate_fractional_year(1980.0) == 1980.0

    def test_validate_fractional_year_invalid(self):
        """Test fractional year validation with invalid values."""
        with pytest.raises(ValidationError, match="Fractional year must be numeric"):
            validate_fractional_year("invalid")
        
        with pytest.raises(ValidationError, match="Fractional year must be between 1980.0 and 2100.0"):
            validate_fractional_year(1900.0)
        
        with pytest.raises(ValidationError, match="Fractional year must be between 1980.0 and 2100.0"):
            validate_fractional_year(2200.0)


class TestGPSTimeValidation:
    """Test GPS time function validation."""

    def test_gps_from_utc_valid(self):
        """Test gpsFromUTC with valid inputs."""
        result = gpsFromUTC(2020, 1, 1, 12, 0, 0)
        assert len(result) == 4
        assert isinstance(result[0], int)  # GPS week
        assert isinstance(result[1], float)  # SOW

    def test_gps_from_utc_invalid_date(self):
        """Test gpsFromUTC with invalid date components."""
        with pytest.raises(GPSTimeError, match="Invalid UTC components"):
            gpsFromUTC(1900, 1, 1, 12, 0, 0)  # Year too early
        
        with pytest.raises(GPSTimeError, match="Invalid UTC components"):
            gpsFromUTC(2020, 13, 1, 12, 0, 0)  # Invalid month

    def test_utc_from_gps_valid(self):
        """Test UTCFromGps with valid inputs."""
        # Test tuple return
        result = UTCFromGps(2086, 388800, dtimeObj=False)
        assert isinstance(result, tuple)
        assert len(result) == 6
        
        # Test datetime return
        result = UTCFromGps(2086, 388800, dtimeObj=True)
        assert isinstance(result, datetime.datetime)

    def test_utc_from_gps_invalid(self):
        """Test UTCFromGps with invalid inputs."""
        with pytest.raises(GPSTimeError, match="Invalid GPS time"):
            UTCFromGps(-1, 388800)  # Negative GPS week
        
        with pytest.raises(GPSTimeError, match="Invalid GPS time"):
            UTCFromGps(2086, 700000)  # SOW too large


class TestFractionalYearValidation:
    """Test fractional year function validation."""

    def test_time_from_yearf_valid(self):
        """Test TimefromYearf with valid inputs."""
        # Valid fractional year
        result = TimefromYearf(2020.5)
        assert isinstance(result, datetime.datetime)
        assert result.year == 2020
        
        # With string formatting
        result = TimefromYearf(2020.5, String="%Y-%m-%d")
        assert isinstance(result, str)
        assert "2020" in result

    def test_time_from_yearf_invalid(self):
        """Test TimefromYearf with invalid inputs."""
        with pytest.raises(FractionalYearError, match="Invalid fractional year"):
            TimefromYearf(1900.0)  # Year too early
        
        with pytest.raises(FractionalYearError, match="Invalid fractional year"):
            TimefromYearf(2200.0)  # Year too late


class TestErrorContexts:
    """Test that error contexts provide useful information."""

    def test_validation_error_context(self):
        """Test that ValidationError includes useful context."""
        try:
            validate_gps_week(-5)
        except ValidationError as e:
            assert "gps_week" in str(e)
            assert "-5" in str(e)

    def test_gps_time_error_propagation(self):
        """Test that GPS time errors properly propagate validation context."""
        try:
            gpsFromUTC(1900, 1, 1, 12, 0, 0)
        except GPSTimeError as e:
            assert "Invalid UTC components" in str(e)
            # Should contain the original validation error information


@pytest.mark.integration
class TestValidationIntegration:
    """Test validation in realistic usage scenarios."""

    def test_roundtrip_with_validation(self):
        """Test that validation doesn't break roundtrip conversions."""
        # Valid UTC time
        year, month, day, hour, minute, second = 2020, 6, 15, 14, 30, 45.123
        
        # Convert to GPS time (should validate inputs)
        gps_week, sow, gps_day, sod = gpsFromUTC(year, month, day, hour, minute, second)
        
        # Convert back to UTC (should validate GPS time)
        utc_dt = UTCFromGps(gps_week, sow, dtimeObj=True)
        
        # Should be very close to original
        original_dt = datetime.datetime(year, month, day, hour, minute, int(second))
        time_diff = abs((utc_dt - original_dt).total_seconds())
        assert time_diff < 1.0  # Within 1 second

    def test_edge_case_validation(self):
        """Test validation with edge cases."""
        # GPS epoch
        result = gpsFromUTC(1980, 1, 6, 0, 0, 0)
        assert result[0] == 0  # Should be GPS week 0
        
        # Leap year edge case
        result = gpsFromUTC(2020, 2, 29, 12, 0, 0)  # Valid leap day
        assert isinstance(result[0], int)
        
        # End of year
        result = gpsFromUTC(2020, 12, 31, 23, 59, 59.999)
        assert isinstance(result[0], int)

    def test_performance_with_validation(self):
        """Test that validation doesn't significantly impact performance."""
        import time
        
        # Time a batch of conversions
        start_time = time.time()
        
        for i in range(1000):
            gps_week, sow, _, _ = gpsFromUTC(2020, 1, 1, 12, 0, i % 60)
            UTCFromGps(gps_week, sow, dtimeObj=True)
        
        elapsed = time.time() - start_time
        
        # Should complete 1000 conversions in reasonable time (< 1 second)
        assert elapsed < 1.0, f"Validation overhead too high: {elapsed:.3f}s"